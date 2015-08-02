from unittest import TestCase
from api_libs.parameters import Dict, Int, Str, VerifyFailed


class DictTestCase(TestCase):
    def test_type(self):
        # Dict parameter 必须指定一个 list 类型的 format spec，且 list item 均为 Parameter
        self.assertRaises(Exception, Dict, "param")
        self.assertRaises(Exception, Dict, "param", format=int)
        self.assertRaises(Exception, Dict, "param", format=Int("param"))

        param = Dict("param", format=[Int("p1"), Str("p2")])
        self.assertEqual(param.verify(dict(param=dict(p1=1, p2="abc"))), dict(p1=1, p2="abc"))

        # 如果有某个子项不是必须的，且没有赋值，那么它不会出现在最终返回的 dict 里
        param = Dict("param", format=[Int("p1", required=False), Str("p2")])
        self.assertEqual(
            param.verify(dict(param=dict(p2="abc"))),
            dict(p2="abc"))

        param = Dict("param", format=[Int("p1", min=10), Str("p2")])
        self.assertRaises(
            VerifyFailed,
            param.verify, dict(param=dict(p1=5, p2="a"))
        )

        # value 中不允许出现 format 中未定义的项
        param = Dict("param", format=[Int("p1")])
        self.assertRaises(VerifyFailed, param.verify, dict(param=dict(p1=5, p2="a")))
