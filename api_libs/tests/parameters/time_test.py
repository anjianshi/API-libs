from unittest import TestCase
from api_libs.parameters import Datetime, Date, VerifyFailed
from datetime import datetime, date


class DatetimeBase:
    param_cls = None

    def batch_match(self, pairs):
        param = self.param_cls("param")
        for input, output in pairs:
            self.assertEqual(param.verify(dict(param=input)), output)

    def batch_not_pass(self, values):
        param = self.param_cls("param")
        for value in values:
            self.assertRaises(
                VerifyFailed, param.verify, dict(param=value))


class DateTimeTestCase(TestCase, DatetimeBase):
    param_cls = Datetime

    def test_type(self):
        self.batch_match([
            (0, datetime.fromtimestamp(0)),
            (0, datetime(1970, 1, 1, 8, 0)),  # 测试时区
            (-1, datetime.fromtimestamp(-1)),
            (100000, datetime.fromtimestamp(100000))
        ])

        self.batch_not_pass([
            "1", "a", True, 1.5
        ])


class DateTestCase(TestCase, DatetimeBase):
    param_cls = Date

    def test_type(self):
        self.batch_match([
            (0, date.fromtimestamp(0)),
            (-1, date.fromtimestamp(-1)),
            (100000, date.fromtimestamp(100000))
        ])

        self.batch_not_pass([
            "1", "a", True, 1.5
        ])
