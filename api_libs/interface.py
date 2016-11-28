from .parameters.Arguments import Arguments

__all__ = ["interface", "Interface"]


def interface(parameters=None):
    """
    :arg parameters:     要生成的 interface 的参数列表
    :type parameters: list of ``api_libs.parameters.Parameter`` or ``None``
    """
    def wrapper(fn):
        return Interface(fn, parameters)
    return wrapper


class Interface:
    def __init__(self, fn, parameters=None):
        self.fn = fn
        self.parameters = parameters

    def __call__(self, arguments={}, **kwargs):
        # 若 interface 不需要参数，arguments 应为 {} 而不是 None
        # 额外的 kwargs 会原样传给原函数

        if self.parameters is not None:
            arguments = Arguments(self.parameters, arguments)
            return self.fn(**kwargs, args=arguments)
        else:
            if arguments != {}:
                raise InterfaceCallFailed("此 interface 不接受任何参数（got: {}）".format(arguments))
            return self.fn(**kwargs)


class InterfaceCallFailed(Exception):
    pass
