from unittest import TestCase
from api_libs.parameters import Bool, VerifyFailed


class BoolTestCase(TestCase):
    def test_type(self):
        param = Bool('param')
        self.assertEqual(param.verify(dict(param=True)), True)
        self.assertEqual(param.verify(dict(param=False)), False)

        for value in [1, 0, '', None]:
            self.assertRaises(VerifyFailed, param.verify, dict(param=value))
