from unittest import TestCase
from api_libs.parameters import Arguments, VerifyFailed, Str, Int, Datetime
from api_libs.parameters.Arguments import ArgumentsError
from datetime import datetime


class ArgumentsTestCase(TestCase):
    def test_Arguments(self):
        parameters = [
            Str("str_param", max_len=3),
            Int("int_param", max=3),
            Datetime("datetime_param"),
            Str("optional_param", required=False)
        ]
        raw_arguments = dict(str_param="ab", int_param=2, datetime_param=100)
        arguments = Arguments(parameters, raw_arguments)

        for key, value in raw_arguments.items():
            if key == "datetime_param":
                value = datetime.fromtimestamp(value)
            # dict like visit
            self.assertEqual(arguments[key], value)
            # object like visit
            self.assertEqual(getattr(arguments, key), value)

        # 未赋值（且不是 required）的 parameter 不应出现在 arguments 中
        self.assertFalse(hasattr(arguments, "optional_param"))
        self.assertFalse("optional_param" in arguments)

    def test_not_pass_Arguments(self):
        parameters = [
            Str("str_param", max_len=3),
            Int("int_param", max=3),
            Datetime("datetime_param")
        ]
        not_pass_data = [
            dict(str_param="abcd", int_param=2, datetime_param=100),
            dict(str_param="abc", int_param=5, datetime_param=100)
        ]
        for raw_arguments in not_pass_data:
            self.assertRaises(VerifyFailed, Arguments, parameters, raw_arguments)

    def test_repeated_parameter(self):
        parameters = [
            Str("param1"),
            Int("param1"),
            Int("param2")
        ]
        self.assertRaisesRegex(
            Exception, "不允许重复定义",
            Arguments, parameters, dict(param1="abc", param2=1))

    def test_unexpected_args(self):
        parameters = [Str("param1")]
        self.assertRaises(ArgumentsError, Arguments, parameters, dict(param1="abc", param2=1))

    def test_future_build(self):
        parameters = [
            Str("p1"),
            Int("p2"),
            Int("p3"),
            Int("p4", required=False)
        ]
        arguments = Arguments(parameters, dict(p1="abc", p2=100, p3=1))

        # 在当前 arguments 值基础上做验证
        self.assertRaises(VerifyFailed, arguments.future_build, [Str("p1", min_len=5)])

        arguments.future_build([Str("p1", min_len=3)])
        self.assertEqual(arguments.p1, "abc")

        # 验证结果写入到当前 arguments
        arguments.future_build([Datetime("p2")])
        self.assertEqual(arguments.p2, datetime.fromtimestamp(100))

        # 能正确地对 parameters 中未给出的部分进行放行
        self.assertEqual(arguments.p3, 1)
        self.assertTrue("p4" not in arguments)
