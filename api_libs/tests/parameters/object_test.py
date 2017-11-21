from unittest import TestCase
from api_libs.parameters import Object, VerifyFailed


class Cla1:
    pass


class Child1(Cla1):
    pass


class Cla2:
    pass


class ObjectTestCase(TestCase):
    def batch_verify(self, passed_values, failed_values, **specs):
        param = Object('param', **specs)
        for value in passed_values:
            self.assertEqual(param.verify(dict(param=value)), value)
        for value in failed_values:
            self.assertRaises(VerifyFailed, param.verify, dict(param=value))

    def test_default_type(self):
        self.batch_verify([False, 0, Cla1()], [])

    def test_cls(self):
        self.batch_verify(
            [Cla1(), Child1()],
            [0, Cla2()],
            type=Cla1
        )
