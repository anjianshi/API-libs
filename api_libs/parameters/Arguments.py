from .Parameter import NoValue
from .utils import ObjectDict


class Arguments(ObjectDict):
    def __init__(self, parameters, arguments):
        self._build(parameters, arguments)

    def _build(self, parameters, arguments, allow_unexpected=False):
        """验证、格式化每一个参数值，并把它们设置成此对象的 property

        :arg Parameter[] parameters: 某个 interface 的参数定义
        :arg dict arguments: 调用者传进来的参数值。dict(name=value, ...)
        """
        parameters = list(parameters)
        param_names = set([param.name for param in parameters])
        if len(param_names) != len(parameters):
            raise Exception("不允许重复定义参数({})".format([param.name for param in parameters]))

        if not allow_unexpected:
            unexpected_args = set(arguments).difference(param_names)
            if len(unexpected_args):
                raise ArgumentsError("不支持以下参数：{}".format(unexpected_args))

        for param in parameters:
            formatted_arg = param.verify(arguments)
            if formatted_arg is not NoValue:
                self[param.name] = formatted_arg

    def future_build(self, parameters):
        """使用新提供的 parameters 定义，对当前 arguments 对象包含的参数值进一步验证、格式化
        需要验证哪些 parameter 就提供哪些即可，不用把当前 arguments 涉及的所有 parameter 都提供出来"""
        self._build(parameters, self, allow_unexpected=True)


class ArgumentsError(Exception):
    pass
