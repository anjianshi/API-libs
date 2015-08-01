from .Parameter import Parameter, VerifyFailed
import datetime

__all__ = ["Datetime", "Date"]


class Datetime(Parameter):
    """把 timestamp (int / float) 类型参数值，转换成 datetime 对象"""
    rule_order = ["type"]

    def rule_type(self, value):
        if type(value) not in [int, float]:
            raise VerifyFailed("参数 {} 的值必须是 timestamp (int / float)，got {} {}".format(
                self.name, type(value), value))
        return datetime.datetime.fromtimestamp(value)


class Date(Parameter):
    """把 timestamp (int / float) 类型参数值，转换成 date 对象"""
    rule_order = ["type"]

    def rule_type(self, value):
        if type(value) not in [int, float]:
            raise VerifyFailed("参数 {} 的值必须是 timestamp (int / float)，got {} {}".format(
                self.name, type(value), value))
        return datetime.date.fromtimestamp(value)
