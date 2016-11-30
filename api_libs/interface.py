from .parameters.Arguments import Arguments

__all__ = ["interface", "bound_interface", "Interface"]


def interface(parameters=None, bound=False):
    """
    :arg parameters:     要生成的 interface 的参数列表
    :arg bound:          用来修饰 bound method（class method、instance method）时，需把此参数设为 True。
                         不然实际被调用时，将无法识别额外传进来的 cls 或 self 参数。
    :type parameters: list of ``api_libs.parameters.Parameter`` or ``None``
    """
    def wrapper(fn):
        return Interface(fn, parameters, bound=bound)
    return wrapper


def bound_interface(parameters=None):
    return interface(parameters, bound=True)


class Interface:
    def __init__(self, fn, parameters=None, bound=False):
        self.fn = fn
        self.parameters = parameters
        self.bound = bound

    def __call__(self, *args, **kwargs):
        return (
            self.bound_call(*args, **kwargs)
            if self.bound
            else self.call(*args, **kwargs)
        )

    # 规范： arguments 没有内容时，应该为 {}，不能为 None
    # 传给 __call__ 的额外的 kwargs 会原样传给原函数

    def call(self, arguments={}, **kwargs):
        if self.parameters is not None:
            arguments = Arguments(self.parameters, arguments)
            return self.fn(**kwargs, args=arguments)
        else:
            if arguments != {}:
                raise InterfaceCallFailed("此 interface 不接受任何参数（got: {}）".format(arguments))
            return self.fn(**kwargs)

    def bound_call(self, cls_or_inst, arguments={}, **kwargs):
        if self.parameters is not None:
            arguments = Arguments(self.parameters, arguments)
            return self.fn(cls_or_inst, **kwargs, args=arguments)
        else:
            if arguments != {}:
                raise InterfaceCallFailed("此 interface 不接受任何参数（got: {}）".format(arguments))
            return self.fn(cls_or_inst, **kwargs)


class InterfaceCallFailed(Exception):
    pass
