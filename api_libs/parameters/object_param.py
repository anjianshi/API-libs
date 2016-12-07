from .Parameter import Parameter, VerifyFailed

__all__ = ["Object"]


class Object(Parameter):
    rule_order = ["type"]

    def spec_defaults(self):
        return dict(
            super().spec_defaults(),
            type=object,
        )

    def rule_type(self, value):
        type = self.specs["type"]

        if not isinstance(value, type):
            raise VerifyFailed("参数 {} 必须是 {} 或其子类的实例".format(self.name, str(type)))

        return value
