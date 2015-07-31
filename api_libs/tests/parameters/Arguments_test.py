from unittest import TestCase
from api_libs.parameters import Arguments, VerifyFailed, Str, Int, Datetime
from api_libs.parameters.Arguments import ArgumentsError
from datetime import datetime


class ArgumentsTestCase(TestCase):
    def test_Arguments(self):
        parameters = [
            Str("str_param", max_len=3),
            Int("int_param", max=3),
            Datetime("datetime_param")
        ]
        raw_arguments = dict(str_param="ab", int_param=2, datetime_param=100)
        arguments = Arguments(parameters, raw_arguments)

        for key, value in raw_arguments.items():
            if key == "datetime_param":
                value = datetime.fromtimestamp(value)
            self.assertEqual(getattr(arguments, key), value)

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

    def test_has_method(self):
        parameters = [
            Str("str_param", max_len=3),
            Int("int_param", max=3),
            Datetime("datetime_param")
        ]
        raw_arguments = dict(str_param="ab", int_param=2, datetime_param=100)
        arguments = Arguments(parameters, raw_arguments)

        self.assertTrue(arguments.has("str_param"))
        self.assertFalse(arguments.has("not_exists_param"))
