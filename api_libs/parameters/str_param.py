from .Parameter import Parameter, VerifyFailed
import re
import html

__all__ = ["Str"]


class Str(Parameter):
    rule_order = ["type", "trim", "regex", "not_regex", "escape"]

    def spec_defaults(self):
        return dict(
            super().spec_defaults(),
            trim=True,
            escape=True
        )

    def rule_type(self, value):
        if type(value) is not str:
            raise VerifyFailed("参数 {} 必须是字符串(got {} {})".format(
                self.name, type(value), value))
        return value

    def rule_trim(self, value):
        """把参数值首尾的空格去掉"""
        return value.strip() if self.specs["trim"] else value

    def rule_choices(self, value):
        if "choices" in self.specs and value not in self.specs["choices"]:
            raise VerifyFailed("rule_choices: 参数 {} 只能为以下值 {} (got: {})".format(
                self.name, self.specs["choices"], value))
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

    def rule_escape(self, value):
        """转义字符串中的 HTML 字符"""
        if self.specs["escape"]:
            value = html.escape(value)
        return value

    def rule_min_len(self, value):
        """通过 min_len=n 指定字符串的最小长度"""
        if "min_len" in self.specs and len(value) < self.specs["min_len"]:
            raise VerifyFailed("参数 {} 的长度不能小于 {} (got: {})".format(
                self.name, self.specs["min_len"], value))
        return value

    def rule_max_len(self, value):
        """通过 min_len=n 指定字符串的最大长度"""
        if "max_len" in self.specs and len(value) > self.specs["max_len"]:
            raise VerifyFailed("参数 {} 的长度不能大于 {} (got: {})".format(
                self.name, self.specs["max_len"], value))
        return value
