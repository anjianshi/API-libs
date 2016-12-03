from .parameters.Arguments import Arguments

__all__ = ["interface", "bound_interface"]


def interface(parameters=None, bound=False):
    """
    :arg parameters:     要生成的 interface 的参数列表
    :arg bound:          用来修饰 bound method（class method、instance method）时，需把此参数设为 True。
                         不然实际被调用时，将无法识别额外传进来的 cls 或 self 参数。
    :type parameters: list of ``api_libs.parameters.Parameter`` or ``None``
    """
    def wrapper(fn):
        # 规范： arguments 没有内容时，应该为 {}，不能为 None
        # 传给 parameters 的额外的 kwargs 会原样传给原函数

        def sort_out_arguments(interface_raw_args, interface_kwargs):
            if parameters is not None:
                return dict(**interface_kwargs, args=Arguments(parameters, interface_raw_args))
            else:
                if interface_raw_args != {}:
                    raise InterfaceCallFailed("此 interface 不接受任何参数（got: {}）".format(interface_raw_args))
                return interface_kwargs

        def interface_fn(arguments={}, **kwargs):
            sorted_args = sort_out_arguments(arguments, kwargs)
            return fn(**sorted_args)

        def bound_interface_fn(cls_or_inst, arguments={}, **kwargs):
            sorted_args = sort_out_arguments(arguments, kwargs)
            return fn(cls_or_inst, **sorted_args)

        choosed_fn = bound_interface_fn if bound else interface_fn
        setattr(choosed_fn, "__api_libs_interface", True)

        return choosed_fn
    return wrapper


def bound_interface(parameters=None):
    return interface(parameters, bound=True)


class InterfaceCallFailed(Exception):
    pass
