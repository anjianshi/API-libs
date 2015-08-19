from unittest import TestCase
from api_libs.parameters import Str, VerifyFailed


class StrTestCase(TestCase):
    def batch_verify(self, passed_values, failed_values, **specs):
        param = Str("param", **specs)
        for value in passed_values:
            self.assertEqual(param.verify(dict(param=value)), value)
            self.assertEqual(
                param.verify(dict(param=" \t " + value + " \n \t")), value)
        for value in failed_values:
            self.assertRaises(VerifyFailed,
                              param.verify, dict(param=value))

    def test_type(self):
        param = Str("param")
        for value in ["", "abc"]:
            self.assertEqual(param.verify(dict(param=value)), value)
        for value in [1, True, b"abc", ["xuz"]]:
            self.assertRaises(VerifyFailed,
                              param.verify, dict(param=value))

    def test_escape(self):
        value_map = {
            # 特殊空白符
            "\ta　　b\tc\t": " a  b c ",

            # HTML 字符
            """<html a="1" b='2'></html>""": "&lt;html a=&quot;1&quot; b=&#x27;2&#x27;&gt;&lt;/html&gt;",

            # SQL 查询字符
            "a%b_c": r"a\%b\_c"
        }

        for input, expected_output in value_map.items():
            self.assertEqual(
                Str("param", trim=False).verify(dict(param=input)),
                expected_output)

        for input in value_map:
            self.assertEqual(
                Str("param", escape=False, trim=False).verify(dict(param=input)),
                input)

    def test_trim(self):
        value = "  \t  asd  def \t \n  "
        result = "asd  def"
        self.assertEqual(
            Str("param").verify(dict(param=value)),
            result)

        self.assertEqual(
            Str("param", escape=False, trim=False).verify(dict(param=value)),
            value)

    def test_min_len(self):
        self.batch_verify(["", "abc"], [], min_len=0)
        self.batch_verify(["dewr", "dewrewer", "abc"], ["", "xx"],  min_len=3)
        # 理论上 min_len 可以设成负数，但实际环境里用不到
        self.batch_verify(["", "abc"], [], min_len=-1)

    def test_max_len(self):
        self.batch_verify([""], ["a", "dd"], max_len=0)
        self.batch_verify(["", "xx", "abc"], ["dewr", "dewrewer"], max_len=3)
        # 理论上 max_len 可以设成负数，但实际环境里用不到
        self.batch_verify([], ["", "abc"], max_len=-1)

    def test_regex(self):
        self.batch_verify(["x-abd", "dabbbc"], ["", "a", "dd"], regex=r"ab+")
        self.batch_verify(
            ["ab", "abbb"], ["", "abc", "dab", "dd"], regex=r"^ab+$")

    def test_not_regex(self):
        self.batch_verify(
            ["xyz", "dd", ""], ["da", "b", "xcc"], not_regex=r"[abc]")
        self.batch_verify(
            ["xyz", "dd", "", ".abc"], ["abc"], not_regex=r"^abc$")
