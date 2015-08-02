from unittest import TestCase
from api_libs.parameters import List, Int, VerifyFailed


class ListTestCase(TestCase):
    def test_type(self):
        # List parameter 必须指定一个 Parameter 类型的 type spec
        self.assertRaises(Exception, List, "param")
        self.assertRaises(Exception, List, "param", type=int)

        param = List("param", type=Int())
        self.assertEqual(param.verify(dict(param=[3, 2, 1])), [3, 2, 1])

        param = List("param", type=Int())
        self.assertEqual(param.verify(dict(param=[])), [])

        param = List("param", type=Int(nullable=True))
        self.assertEqual(param.verify(dict(param=[3, None, 1])), [3, None, 1])

        param = List("param", type=Int())
        self.assertRaises(VerifyFailed, param.verify, dict(param=["abc", 2, 1]))

        param = List("param", type=Int(max=2))
        self.assertRaises(VerifyFailed, param.verify, dict(param=[3, 2, 1]))

    def batch_verify(self, passed_values, failed_values, **specs):
        param = List("param", type=Int(), **specs)
        for value in passed_values:
            self.assertEqual(param.verify(dict(param=value)), value)
        for value in failed_values:
            self.assertRaises(VerifyFailed, param.verify,
                              dict(param=value))

    def test_min_len(self):
        self.batch_verify(
            [[3, 2, 1], [5, 4, 3, 2, 1]],
            [[], [1], [1, 2]],
            min_len=3)

        self.batch_verify(
            [[], [3, 2, 1], [5, 4, 3, 2, 1]],
            [],
            min_len=0)

        self.batch_verify(
            [[], [3, 2, 1], [5, 4, 3, 2, 1]],
            [],
            min_len=-1)

    def test_max_len(self):
        self.batch_verify(
            [[], [1], [1, 2]],
            [[5, 4, 3]],
            max_len=2)

        self.batch_verify(
            [[]],
            [[3, 2, 1], [5, 4, 3, 2, 1]],
            max_len=0)

        self.batch_verify(
            [],
            [[], [3, 2, 1], [5, 4, 3, 2, 1]],
            max_len=-1)
