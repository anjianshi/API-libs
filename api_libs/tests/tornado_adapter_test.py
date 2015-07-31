from tornado.web import Application
from tornado.testing import AsyncHTTPTestCase
import json
import urllib.parse
from api_libs.adapters.tornado_adapter import TornadoAdapter
from api_libs.parameters import *
from api_libs.route import Router, Context


class BaseTestCase(AsyncHTTPTestCase):
    def setUp(self):
        self.adapter = self.get_adapter()
        super().setUp()

    def get_adapter(self):
        raise Exception("未实现")

    def get_app(self):
        return Application([
            ("/(.+)", self.adapter.RequestHandler),
        ], debug=1)

    def parse_resp(self, resp):
        return json.loads(resp.body.decode()) if resp.body is not None else None


class TornadoAdapterTestCase(BaseTestCase):
    def get_adapter(self):
        return TornadoAdapter()

    def test_request_adapte(self):
        """测试是否能正常地根据 HTTP Request 调用对应的 API"""
        result = dict(called=False)

        @self.adapter.api_router.register("test.path")
        def fn(context):
            result["called"] = True

        self.fetch("/test.path")
        self.assertEqual(result["called"], True)

    def test_response_formatter(self):
        """测试是否能正确地把 API 的返回值格式化并输出
        默认会把返回值转换成 JSON 格式"""
        @self.adapter.api_router.register("test.path")
        def fn(context):
            return dict(data=[1, 2, 3])

        resp = self.fetch("/test.path")
        self.assertEqual(self.parse_resp(resp), dict(data=[1, 2, 3]))

    def test_method_support(self):
        @self.adapter.api_router.register("test.path")
        def fn(context):
            return True

        resp = self.fetch("/test.path", method="GET")
        self.assertEqual(self.parse_resp(resp), True)

        resp = self.fetch("/test.path", method="POST", body="")
        self.assertEqual(self.parse_resp(resp), True)

        resp = self.fetch("/test.path", method="PUT", body="")
        self.assertEqual(resp.code, 405)

        resp = self.fetch("/test.path", method="DELETE")
        self.assertEqual(resp.code, 405)

    def test_arguments_parse(self):
        @self.adapter.api_router.register(
            "test.path", [Int("argx"), Int("argy", default=5)])
        def fn(context, arguments):
            return {"data": arguments.argx * arguments.argy}

        # arguments in post body
        resp = self.fetch("/test.path", method="POST", body='{"argx": 20}')
        self.assertEqual(self.parse_resp(resp), {"data": 100})

        # arguments in post form data
        body = urllib.parse.urlencode(dict(arguments='{"argx": 30}'))
        resp = self.fetch("/test.path", method="POST", body=body)
        self.assertEqual(self.parse_resp(resp), {"data": 150})

        # arguments in url query string
        resp = self.fetch('/test.path?arguments={"argx":40}')
        self.assertEqual(self.parse_resp(resp), {"data": 200})

        # 如果从多种渠道给出 arguments，只有其中一种会被使用
        # 下面的请求中，通过 post body 传递的 argx 和 argy 的值不会被使用
        resp = self.fetch('/test.path?arguments={"argx":50}',
                          method="POST", body='{"argx": 1, "argy": 2}')
        self.assertEqual(self.parse_resp(resp), {"data": 250})

        def test_context(self):
            @self.adapter.api_router.register("test.path")
            def fn(context):
                self.assertIsInstance(context.req_handler, self.adapter.RequestHandler)
                return True

            resp = self.fetch("/test.path")
            self.assertEqual(self.parse_resp(resp), True)

    def test_bind_router(self):
        """测试 bind_router() 方法是否正常工作"""
        router = Router()
        self.assertNotEqual(self.adapter.api_router, router)

        self.adapter.bind_router(router)
        self.assertEqual(self.adapter.api_router, router)


class TornadoAdapterCustomFormatterTestCase(BaseTestCase):
    def get_adapter(self):
        return TornadoAdapter(output_formatter=self.format)

    def format(self, value):
        """这个自定义的 foramtter 会把所有值都转换成如下字符串"""
        return "format result"

    def test_customer_formatter(self):
        @self.adapter.api_router.register("test.path")
        def fn(context):
            return [1, 2, 3]

        resp = self.fetch("/test.path")
        self.assertEqual(resp.body.decode(), "format result")


class TornadoAdapterCustomRouterTestCase(BaseTestCase):
    def get_adapter(self):
        class MyContext(Context):
            def __init__(self, router, req_handler):
                self.req_handler = req_handler
                super().__init__(router)

        router = Router(MyContext)

        @router.register("test.path.1")
        def fn(context):
            self.assertIsInstance(context, MyContext)
            return True

        adapter = TornadoAdapter(api_router=router)

        @adapter.api_router.register("test.path.2")
        def fn(context):
            self.assertIsInstance(context, MyContext)
            return True

        return adapter

    def test_custom_router(self):
        """测试 adapter 能否正常处理手动指定的 router"""
        resp = self.fetch("/test.path.1")
        self.assertEqual(self.parse_resp(resp), True)

        resp = self.fetch("/test.path.2")
        self.assertEqual(self.parse_resp(resp), True)



