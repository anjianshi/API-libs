from .Parameter import Parameter, VerifyFailed
import re

__all__ = ["Str"]


class Str(Parameter):
    """default specs: trim=True"""
    rule_order = ["type", "trim"]

    def rule_type(self, value):
        if type(value) is not str:
            raise VerifyFailed("参数 {} 必须是字符串(got {} {})".format(
                self.name, type(value), value))
        return value

    def rule_trim(self, value):
        """把参数值首尾的空格去掉"""
        return value.strip() if self.specs.get("trim", True) else value

    def rule_min_len(self, value):
        """通过 min_len=n 指定字符串的最小长度"""
        if "min_len" in self.specs and len(value) < self.specs["min_len"]:
            raise VerifyFailed("参数 {} 的长度必须大于 {} (got: {})".format(
                self.name, self.specs["min_len"], value))
        return value

    def rule_max_len(self, value):
        """通过 min_len=n 指定字符串的最大长度"""
        if "max_len" in self.specs and len(value) > self.specs["max_len"]:
            raise VerifyFailed("参数 {} 的长度不能大于 {} (got: {})".format(
                self.name, self.specs["max_len"], value))
        return value

    def rule_regex(self, value):
        if "regex" in self.specs and not re.search(self.specs["regex"], value):
            raise VerifyFailed("rule_regex: 参数 {} 不符合格式(got: {})".format(
                self.name, value))
        return value

    def rule_not_regex(self, value):
        if "not_regex" in self.specs and re.search(self.specs["not_regex"], value):
            raise VerifyFailed("rule_not_regex: 参数 {} 不符合格式(got: {})".format(
                self.name, value))
        return value
