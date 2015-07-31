from .Parameter import NoValue


class Arguments:
    def __init__(self, parameters, arguments):
        """验证、格式化每一个参数值，并把它们设置成此对象的 property

        :arg Parameter[] parameters: 某个 API 的参数定义
        :arg dict arguments: 调用者传进来的参数值。dict(name=value, ...)
        """
        param_names = set([param.name for param in parameters])
        if len(param_names) != len(parameters):
            raise Exception("不允许重复定义参数")

        unexpected_args = set(arguments).difference(param_names)
        if len(unexpected_args):
            raise ArgumentsError("不支持以下参数：{}".format(unexpected_args))

        for param in parameters:
            formatted_arg = param.verify(arguments)
            if formatted_arg is not NoValue:
                setattr(self, param.name, formatted_arg)


class ArgumentsError(Exception):
    pass
