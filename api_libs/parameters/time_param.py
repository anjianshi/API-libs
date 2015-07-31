from .Parameter import Parameter, VerifyFailed
import datetime

__all__ = ["Datetime", "Date"]


class Datetime(Parameter):
    """把 int 类型（timestamp）的参数值，转换成 datetime 对象"""
    rule_order = ["type"]

    def rule_type(self, value):
        if type(value) is not int:
            raise VerifyFailed("参数 {} 的值必须是 timestamp (int)，got {} {}".format(
                self.name, type(value), value))
        return datetime.datetime.fromtimestamp(value)


class Date(Parameter):
    """把 int 类型（timestamp）的参数值，转换成 date 对象"""
    rule_order = ["type"]

    def rule_type(self, value):
        if type(value) is not int:
            raise VerifyFailed("参数 {} 的值必须是 timestamp (int)，got {} {}".format(
                self.name, type(value), value))
        return datetime.date.fromtimestamp(value)
