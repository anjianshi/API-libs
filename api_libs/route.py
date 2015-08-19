import re
from .parameters.Arguments import Arguments

__all__ = ["Router", "Context", "Handler"]


class Router:
    """通过此对象注册、调用 API handler"""

    def __init__(self, context_cls=None):
        """:arg context_cls: 此 router 绑定的 context 类型。不同类型的 context 提供不同的功能。
        :type context_cls: `Context` 或它的子类"""
        self.context_cls = context_cls or Context
        self.handlers = {
            # path: handler
        }

    def register(self, path, parameters=None):
        """通过这个 decorator 注册 API

        :arg string path: API 对应的 route path
        :arg parameters: 此 API 的参数定义，如果不需要参数，则为 None
        :type parameters: list of ``api_libs.parameters.Parameter`` or ``None``
        """
        if type(path) != str:
            raise APIRegisterFailed("API path ({}) 必须是字符串".format(path))

        path = path.lower()

        if re.search("/", path):
            raise APIRegisterFailed("API path 中不允许出现 '/' 字符(got: {})".format(path))
        elif path in self.handlers:
            raise APIRegisterFailed("API path ({}) 已存在，不允许重复添加".format(path))

        def wrapper(handler_func):
            handler = Handler(handler_func, parameters)
            self.handlers[path] = handler
            return handler
        return wrapper

    def call(self, path, context_data=None, arguments={}):
        """调用 API

        :arg string path: 要调用的 API 的 router path
        :arg any context_data: 初始化 context 对象所需的数据，不同类型的 context 需要不同类型的数据
        :arg dict arguments: 传给 API 的参数值。router 会根据 API 的参数定义对参数值进行检查、格式化"""
        context_instance = self.context_cls(self, context_data)
        return self._call_with_context(path, context_instance, arguments)

    def _call_with_context(self, path, context_instance, arguments={}):
        if type(path) != str:
            raise APICallFailed("API path ({}) 必须是字符串".format(path))

        path = path.lower()

        if not isinstance(context_instance, self.context_cls):
            raise APICallFailed("context 类型错误（expect: {}, got: {}）".format(self.context_cls, context_instance))
        if path not in self.handlers:
            raise APICallFailed("API '{}' 不存在".format(path))
        return self.handlers[path](context_instance, arguments)

    def change_context(self, context_cls):
        """为当前 router 指定一个新的 context 类型"""
        self.context_cls = context_cls


class Context:
    """存放 API 被调用时的上下文信息，以及提供一些辅助方法"""
    def __init__(self, router, context_data=None):
        self.router = router
        self.data = context_data

    def call(self, api_path, arguments={}):
        """调用另一个 API。
        新调用的 API 会接收到和当前一样的 context 对象。"""
        return self.router._call_with_context(api_path, self, arguments)


class Handler:
    def __init__(self, handler_func, parameters=None):
        self.handler_func = handler_func
        self.parameters = parameters

    def __call__(self, context, arguments={}):
        """若 API 不需要参数，arguments 应为 {} 而不是 None"""

        if self.parameters is not None:
            arguments = Arguments(self.parameters, arguments)
            return self.handler_func(context, arguments)
        else:
            if arguments != {}:
                raise APICallFailed("此 API 不接受任何参数（got: {}）".format(arguments))
            return self.handler_func(context)


class APIRegisterFailed(Exception):
    pass


class APICallFailed(Exception):
    pass
