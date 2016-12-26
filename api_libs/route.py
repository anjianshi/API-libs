import re
from .interface import interface as to_interface

__all__ = ["Router", "Context"]


class Router:
    """通过此对象集中管理（注册、调用）interface"""

    def __init__(self, context_cls=None):
        """
        :arg context_cls: 此 router 绑定的 context 类型。不同类型的 context 提供不同的功能。
        :type context_cls: `Context` 或它的子类
        """
        self.context_cls = context_cls or Context
        self.interfaces = {
            # path: interface
        }

    def register(self, path, parameters=None, bound=False):
        """通过这个 decorator 注册 interface。
        可以传入一个普通函数，此 decorator 会自动将其转换为 interface；也可以传入一个已经生成好的 interface。

        :arg string path: interface 对应的 route path
        :arg parameters: 只在传入的是普通函数（也就是不是 interface）时有效, 指定其参数定义，如果不需要参数，则为 None。
        :arg parameters: 只在传入的是普通函数（也就是不是 interface）时有效，指明当前传入的是 function 还是 bound method。
        :type parameters: list of ``api_libs.parameters.Parameter`` or ``None``
        """
        if type(path) != str:
            raise RouteRegisterFailed("route path ({}) 必须是字符串".format(path))

        path = path.lower()

        if re.search("/", path):
            raise RouteRegisterFailed("route path 中不允许出现 '/' 字符(got: {})".format(path))
        elif path in self.interfaces:
            raise RouteRegisterFailed("route path ({}) 已存在，不允许重复添加".format(path))

        def wrapper(interface_or_fn):
            if hasattr(interface_or_fn, "__api_libs_interface"):
                interface = interface_or_fn
            else:
                interface = to_interface(parameters, bound)(interface_or_fn)

            self.interfaces[path] = interface
            return interface
        return wrapper

    def call(self, path, context_data=None, arguments={}):
        """调用 interface

        :arg string path: 要调用的 interface 的 router path
        :arg any context_data: 可以是初始化 context 对象所需的数据，也可以直接传入 context 实例。不同类型的 context 需要不同类型的数据
        :arg dict arguments: 传给 interface 的参数值"""
        context_instance = context_data if isinstance(context_data, self.context_cls) else self.context_cls(self, context_data)
        return self._call_with_context(path, context_instance, arguments)

    def _call_with_context(self, path, context_instance, arguments={}):
        if type(path) != str:
            raise RouteCallFailed("route path ({}) 必须是字符串".format(path))

        path = path.lower()

        if not isinstance(context_instance, self.context_cls):
            raise RouteCallFailed("context 类型错误（expect: {}, got: {}）".format(self.context_cls, context_instance))
        if path not in self.interfaces:
            raise RouteCallFailed("route '{}' 不存在".format(path))
        return self.interfaces[path](arguments=arguments, context=context_instance)

    def change_context(self, context_cls):
        """为当前 router 指定一个新的 context 类型"""
        self.context_cls = context_cls


class Context:
    """存放 interface 被调用时的上下文信息，以及提供一些辅助方法"""
    def __init__(self, router, context_data=None):
        self.router = router
        self.data = context_data

    def call(self, route_path, arguments={}):
        """调用同一个 router 下的另一个 interface。
        新调用的 interface 会接收到和当前一样的 context 对象。"""
        return self.router._call_with_context(route_path, self, arguments)


class RouteRegisterFailed(Exception):
    pass


class RouteCallFailed(Exception):
    pass
