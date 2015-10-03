from .Parameter import Parameter, VerifyFailed
import datetime

__all__ = ["Datetime", "Date"]


class Datetime(Parameter):
    """把 timestamp (int / float) 类型参数值，转换成 datetime 对象"""
    rule_order = ["type"]

    def rule_type(self, value):
        if type(value) is datetime.datetime:
            return value
        elif type(value) in [int, float]:
            return datetime.datetime.fromtimestamp(value)
        else:
            raise VerifyFailed("参数 {} 的值必须是 timestamp (int / float / datetime.datetime)，got {} {}".format(
                               self.name, type(value), value))


class Date(Parameter):
    """把 timestamp (int / float) 类型参数值，转换成 date 对象"""
    rule_order = ["type"]

    def rule_type(self, value):
        if type(value) is datetime.date:
            return value
        elif type(value) in [int, float]:
            return datetime.date.fromtimestamp(value)
        else:
            raise VerifyFailed("参数 {} 的值必须是 timestamp (int / float / datetime.date)，got {} {}".format(
                               self.name, type(value), value))
