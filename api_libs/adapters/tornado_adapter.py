from tornado.web import RequestHandler
import tornado.concurrent
import json
import asyncio
from .. import APILibError
from ..route import Router, Context

__all__ = ['TornadoAdapter']


class TornadoContext(Context):
    '''
    Attributes:

    * req_handler: 与当前 HTTP Request 对应的 `tornado.web.RequestHandler` 实例
    '''
    def __init__(self, router, req_handler):
        self.req_handler = req_handler
        super().__init__(router)


def dump_json(result, req_handler):
    req_handler.set_header('Content-Type', 'application/json')
    return json.dumps(result)


class TornadoAdapter:
    '''将 router 与 Tornado app 进行适配。
    通过此对象把 HTTP Request 转换成 interface 调用；再把调用结果输出给客户端

    Attributes:

    * router: 此 adapter 绑定的 router。通过把 router 绑定到 adapter，使其中的 interface 能通过 HTTP Request 进行调用。

    * RequestHandler: 经过特殊调整，能够把 HTTP Request 转换成 interface 调用的 RequestHandler。
      应把它加入 tornado application 的 handler 列表里，分配一个 url pattern

      注意：必须保证 url pattern 中有且只有一个 regex group，代表 route path
      例如这样: (r'/api/(.+)', RequestHandler)

      此 RequestHandler 只响应 GET 和 POST 请求

    adapter 的使用方法见 README.md 中的示例代码
    '''
    def __init__(self, router=None, output_formatter=dump_json):
        '''
        :arg router: 指定要把 adapter 绑定到哪个 router。
          若未指定此此参数，adapter 会自己创建一个。
          注意，adapter 要求与它绑定的 router 的 Context 类型能够接收一个 tornado RequestHandler 实例作为 context data

        :arg output_formatter: RequestHandler 会调用此函数对 interface 的返回值进行格式化后，再把得到的内容输出给客户端。
          默认是转换成 JSON，你可以自己指定一个函数，来转换成其他格式。
          此函数会接收到两个参数： call result 和 RequestHandler 对象。第二个参数用来输出自定义的 HTTP Header
        '''
        self.output_formatter = output_formatter
        self.router = router or Router(TornadoContext)

        class AdaptedRequestHandler(RequestHandler):
            '''
            为了支持异步行为，handler 以 async 函数的方式运行。
            不过 interface 并不要求非得是 async 函数，即使是普通函数，handler 也能正常处理。
            '''
            async def get(handler_self, route_path):
                await self.handle_request(handler_self, route_path)

            async def post(handler_self, route_path):
                await self.handle_request(handler_self, route_path)

        self.RequestHandler = AdaptedRequestHandler

    def bind_router(self, router):
        '''将 adapter 绑定到另一个 router 上
        注意，与新的 router 绑定后，原来的 router 中注册的 interfaces，并不会转移到新的 router 里。
        如果有需要，请手动进行转移（new_router.interfaces = {path:interface for path, interface in old_router.interfaces.items()}）
        '''
        self.router = router

    async def handle_request(self, req_handler, route_path):
        '''进行 HTTP Request 与 interface Call 与 JSON Response 之间的转换

        HTTP 请求的格式约定
        要调用一个 interface，需要三样东西：
            1. route path
            2. context data
            3. arguments
        通过 HTTP 请求调用 interface 时，
            - route path 通过 URL 指定
            - context data 会被设置为当前的 tornado RequestHandler，不需要手动指定
            - arguments 通过 query string 或 POST body 指定，详见 `extract_arguments()` 方法
        '''
        arguments = self.extract_arguments(req_handler)
        result = await self.call_interface(req_handler, route_path, arguments)
        self.finish_request(req_handler, result)

    async def call_interface(self, req_handler, route_path, arguments):
        '''这里把对 interface 的调用单独拆分出一个方法，是为了让使用者能方便地对此行为进行扩展
        例如在执行调用前进行一些准备操作'''
        ret_val = self.router.call(route_path, req_handler, arguments)
        if asyncio.iscoroutine(ret_val) or isinstance(ret_val, tornado.concurrent.Future):
            ret_val = await ret_val
        return ret_val

    def finish_request(self, req_handler, result):
        output = self.output_formatter(result, req_handler)
        req_handler.write(output)

    def extract_arguments(self, req_handler):
        '''从 HTTP Request 中提取出 arguments

        arguments 必须以 JSON 的形式提供。
        可以用来提供 values 的渠道有三种，分别对应不同的情况：
            1. POST body
               把 arguments json 作为 POST body
               并将 HTTP Header 中的 Content-Type 设为 application/json
               大部分情况下，使用这种模式

            2. POST field
               在 POST 请求中，创建一个名为 arguments 的 field，把 arguments json 作为它的的值
               适用于在同一个请求中，既要提交 argumens 又要上传文件的情况

            3. query string
               在 URL query string 中指定一个名为 arguments 的项，把 argument json 作为它的值。
               适用于没法提交 POST 请求，又必须指定 arguments 的情况，例如向用户的手机或邮箱发送的验证链接。
               用这种方式，arguments 的内容不能太长。
        如果同时从多种渠道提供了 arguments ，那么只有其中一种会被使用。

        之所以强制使用 JSON 的格式，不支持传统的 query string 和 POST form-data，
        是因为传统的 form 处理起来问题太多，而且只支持字符串类型；JSON 的数据结构则简单、清晰，类型丰富，可以减少很多麻烦。
        '''
        raw_arguments = req_handler.get_argument('arguments', default='')
        # 这里不能直接用 == 'application/json' 进行判断，因为有些客户端（例如 React Native）会在原 Content-Type 后面加上额外的 ;charset=utf-8 之类的文字。
        if raw_arguments == '' and req_handler.request.headers.get('Content-Type', '').startswith('application/json'):
            try:
                raw_arguments = req_handler.request.body.strip().decode()
            except UnicodeDecodeError:
                # request body 中包含了无法识别的字符（例如二进制数据）
                raise RequestHandleFailed('arguments 中包含非法字符')

        if len(raw_arguments):
            try:
                arguments = json.loads(raw_arguments)
                if type(arguments) is not dict:
                    raise ValueError()
            except ValueError:
                # Python 3.5 里，json 抛出的异常变成了 JSONDecodeError，不过它貌似是 ValueError 的子类，所以依然可以这样捕获
                raise RequestHandleFailed('arguments 格式不合法: ' + raw_arguments)
        else:
            arguments = {}
        return arguments


class RequestHandleFailed(APILibError):
    pass
