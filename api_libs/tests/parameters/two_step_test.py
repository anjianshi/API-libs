from unittest import TestCase
from api_libs.parameters import CanHas, CantNotHas, VerifyFailed, NoValue, Arguments, Datetime
from datetime import datetime


class TwoStepParameterTestCase(TestCase):
    def test_can_has(self):
        param = CanHas("p1")

        # 可以赋任意类型的值
        self.assertEqual(param.verify(dict(p1=1)), 1)
        self.assertEqual(param.verify(dict(p1="abc")), "abc")
        # 可以赋 None 值
        self.assertEqual(param.verify(dict(p1=None)), None)
        # 可以不赋值
        self.assertEqual(param.verify(dict()), NoValue)

    def test_can_not_has(self):
        param = CantNotHas("p1")

        self.assertEqual(param.verify({}), NoValue)
        self.assertRaises(VerifyFailed, param.verify, dict(p1=1))
        # None 值也不允许通过
        self.assertRaises(VerifyFailed, param.verify, dict(p1=None))

    def test_collection(self):
        """测试 CanHas、CanNotHas 和 Arguments.future_build() 搭配使用"""

        arguments = Arguments(
            [CanHas("p1"), CanHas("p2"), CanHas("p3")],
            dict(p1=1, p2=2))

        arguments.future_build([Datetime("p1")])
        self.assertEqual(arguments.p1, datetime.fromtimestamp(1))

        self.assertRaises(VerifyFailed, arguments.future_build, [CantNotHas("p2")])

        arguments.future_build([CantNotHas("p3")])
        self.assertTrue("p3" not in arguments)
