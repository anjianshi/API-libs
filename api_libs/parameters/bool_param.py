from .Parameter import Parameter, VerifyFailed

__all__ = ["Bool"]


class Bool(Parameter):
    def rule_type(self, value):
        if type(value) is not bool:
            raise VerifyFailed("参数 {} 的值必须为 True 或 False (got: {})".format(
                self.name, value))
        return value
