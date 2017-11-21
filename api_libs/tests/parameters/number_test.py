from unittest import TestCase
from api_libs.parameters import Int, Float, Decimal, VerifyFailed
import decimal as dec


class NumTestCase:
    '''传入 arguments 时，不需要用 value_cls 进行包裹，这部分应该用什么类型的数值都能正常运行
    只有在比对返回值时，才要用 value_cls'''

    param_cls = None
    value_cls = None

    def match(self, value, expect_value):
        # 通过此方法可以检查两个 value 是否数值相等，类型也相同
        # 例如 Decimal 和 int，通过 == 操作符没法检查类型
        # 如果用 is 操作符，更是永远返回 False
        # 所以只好创建一个方法，手动检查类型
        self.assertEqual(value, expect_value)
        self.assertEqual(type(value), type(expect_value))

    def batch_verify(self, passed_values, failed_values, **specs):
        param = self.param_cls('param', **specs)
        for value in passed_values:
            self.match(param.verify(dict(param=value)), self.value_cls(value))
        for value in failed_values:
            self.assertRaises(VerifyFailed, param.verify,
                              dict(param=value))

    def test_min(self):
        self.batch_verify(range(5, 10), range(-1, 4), min=5)
        self.batch_verify(range(0, 5), range(-5, -1), min=0)
        self.batch_verify(range(-2, 1), range(-10, -3), min=-2)

    def test_max(self):
        self.batch_verify(range(-1, 5), range(6, 10), max=5)
        self.batch_verify(range(-5, 0), range(1, 5), max=0)
        self.batch_verify(range(-10, -2), range(-1, 1), max=-2)

    def test_nozero(self):
        # 默认允许 0
        self.match(self.param_cls('param').verify(dict(param=0)),
                   self.value_cls(0))

        self.batch_verify([-2, -1, 1, 2, 3], [-3, 0, 4],
                          min=-2, max=3, nozero=True)


class IntTestCase(TestCase, NumTestCase):
    param_cls = Int
    value_cls = int

    def test_type(self):
        param = Int('param')

        self.match(param.verify(dict(param=10)), 10)

        for value in [10.1, dec.Decimal(5),
                      float('nan'), float('inf'), float('-inf'),
                      '10', True, [1]]:
            self.assertRaises(
                VerifyFailed, param.verify, dict(param=value))


class FloatTestCase(TestCase, NumTestCase):
    param_cls = Float
    value_cls = float

    def test_type(self):
        param = Float('param')

        for value in [10, 11.1, 0.1]:
            self.match(param.verify(dict(param=value)), float(value))

        for value in [dec.Decimal(5),
                      float('nan'), float('inf'), float('-inf'),
                      '10', '0.1', True, [1]]:
            self.assertRaises(
                VerifyFailed, param.verify, dict(param=value))


class DecimalTestCase(TestCase, NumTestCase):
    param_cls = Decimal
    value_cls = dec.Decimal

    def test_type(self):
        param = Decimal('param')

        for value in ['10', '0.1', 10, dec.Decimal(1), 11.1]:
            self.match(param.verify(dict(param=value)), dec.Decimal(str(value)))

        self.match(param.verify(dict(param=0.1)), dec.Decimal('0.1'))

        for value in [dec.Decimal('nan'), dec.Decimal('inf'),
                      dec.Decimal('-inf'), 'nan', 'abc', True, [1]]:
            self.assertRaises(
                VerifyFailed, param.verify, dict(param=value))
