from .Parameter import Parameter, VerifyFailed
import math
import decimal as dec

__all__ = ["Int", "Float", "Decimal"]


class Number(Parameter):
    """各数值类型 Parameter 的基类，不建议直接使用"""

    def spec_defaults(self):
        return dict(
            super().spec_defaults(),
            nozero=False
        )

    def rule_min(self, value):
        """通过 min=n 指定最小值"""
        if "min" in self.specs and value < self.specs["min"]:
            raise VerifyFailed("参数 {} 的值不能小于 {} (got: {})".format(
                self.name, self.specs["min"], value))
        return value

    def rule_max(self, value):
        """通过 max=n 指定最大值"""
        if "max" in self.specs and value > self.specs["max"]:
            raise VerifyFailed("参数 {} 的值不能大于 {} (got: {})".format(
                self.name, self.specs["max"], value))
        return value

    def rule_nozero(self, value):
        """通过 nozero=true/false 指定是否允许等于 0"""
        if self.specs["nozero"] and value == 0:
            raise VerifyFailed("参数 {} 不能等于 0".format(self.name))
        return value


class Int(Number):
    rule_order = ["type"]

    def rule_type(self, value):
        if type(value) is not int or math.isnan(value) or math.isinf(value):
            raise VerifyFailed("参数 {} 必须是合法的 int (got: {} {})".format(
                self.name, type(value), value))
        return value


class Float(Number):
    rule_order = ["type"]

    def rule_type(self, value):
        if type(value) not in [int, float] or math.isnan(value) or math.isinf(value):
            raise VerifyFailed("参数 {} 必须是合法的 int 或 float (got: {} {})".format(
                self.name, type(value), value))
        # 如果传入的数值是 int，此操作会将其强制转换成 float
        return float(value)


class Decimal(Number):
    rule_order = ["type"]

    def rule_type(self, value):
        if type(value) is str:
            try:
                dec_value = dec.Decimal(value)
            except dec.InvalidOperation:
                raise VerifyFailed("参数 {} 的值({})不符合格式".format(self.name, value))
        elif type(value) is int:
            dec_value = dec.Decimal(value)
        elif type(value) is float:
            # float 在转换成 decimal 前，必须先转换成字符串。不然会有精度损失。例如： Decimal(0.18) 会得到 0.179999...
            dec_value = dec.Decimal(str(value))
        elif type(value) is dec.Decimal:
            dec_value = value
        else:
            raise VerifyFailed("参数 {} 的原始值必须是 str、int、float、Decimal, got {} {}".format(
                self.name, type(value), value))

        if math.isnan(dec_value) or math.isinf(dec_value):
            raise VerifyFailed("参数 {} 的值({})不符合格式".format(self.name, value))

        return dec_value
