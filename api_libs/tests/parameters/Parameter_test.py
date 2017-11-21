from unittest import TestCase
from api_libs.parameters import VerifyFailed
from api_libs.parameters.Parameter import Parameter, NoValue, Remove


class ParameterTestCase(TestCase):
    def test_define_parameter(self):
        param1 = Parameter('param1')
        self.assertEqual(param1.name, 'param1')
        self.assertEqual(param1.specs, Parameter.spec_defaults(None))

        param2_specs = dict(nullable=True, default=10, cust_spec='cust_val')
        param2 = Parameter('param2', **param2_specs)
        self.assertEqual(param2.name, 'param2')
        self.assertEqual(param2.specs, dict(Parameter.spec_defaults(None), **param2_specs))

    def test_copy(self):
        param = Parameter(
            'my_param', nullable=True, default=20, cust_spec='cust_val')

        def test_copy(copy, expected_name, expected_specs):
            self.assertEqual(copy.name, expected_name)
            self.assertEqual(copy.specs, expected_specs)

        # 完全复制
        copy1 = param.copy()
        self.assertNotEqual(copy1, param)
        self.assertEqual(type(copy1), type(param))
        test_copy(copy1, param.name, param.specs)

        # 重命名复制
        test_copy(param.copy('copy_param2'), 'copy_param2', param.specs)

        # remove specs
        test_copy(param.copy('copy_param3', cust_spec=NoValue),
                  'copy_param3', dict(Parameter.spec_defaults(None), default=20, nullable=True))
        test_copy(param.copy('copy_param3', cust_spec=Remove),
                  'copy_param3', dict(Parameter.spec_defaults(None), default=20, nullable=True))

        # inplace specs
        test_copy(
            param.copy('copy_param4', nullable=NoValue, new_spec=1, cust_spec='updated_val'),
            'copy_param4',
            dict(Parameter.spec_defaults(None), default=20, new_spec=1, cust_spec='updated_val'))

        # copy by __call__
        param = Parameter('my_param', a=1, b=2)
        test_copy(
            param('p2'),
            'p2', dict(Parameter.spec_defaults(None), a=1, b=2)
        )
        test_copy(
            param(a=NoValue, b=3, c=4),
            'my_param', dict(Parameter.spec_defaults(None), b=3, c=4)
        )
        test_copy(
            param('p2', b=3, c=4),
            'p2', dict(Parameter.spec_defaults(None), a=1, b=3, c=4)
        )

    def test_verify_method_and_sysrule_default(self):
        param = Parameter('param1', default=10)
        # 1. default 的执行顺序应该在 required 前面，所以 required 不会在填充默认值之前就进行检查，导致误报。
        # 2. default 对参数值的更新能够传递到 required 那里，这样它才会认为参数是有值的
        # 3. 通过所有验证后，经过调整的参数值会被返回给调用者
        self.assertEqual(param.verify({}), 10)

    def test_sysrule_required(self):
        param = Parameter('myparam')

        # 赋了值的情况下，能够正常通过检查
        self.assertEqual(param.verify(dict(myparam='xyz')), 'xyz')

        # required 默认应为 True，所以这里应该验证失败
        self.assertRaises(VerifyFailed, param.verify, {})

        # 手动设置 required 为 True 的结果应该和使用默认值时一样
        param2 = Parameter('myparam2', required=True)
        self.assertRaises(VerifyFailed, param2.verify, {})

        # 若 reuired 为 False，则不会抛出异常。且因为没有指定默认值，所以最终会返回 NoValue
        param3 = Parameter('myparam3', required=False)
        self.assertEqual(param3.verify({}), NoValue)

        # 在 required 为 False 的情况下，如果给出了参数值，仍能正确返回参数值
        param4 = Parameter('myparam4', required=False)
        self.assertEqual(param4.verify(dict(myparam4='123')), '123')

        # 只要参数有值，即使值为 None，也应该能通过 required 的检查
        # (但这样子通不过 nullable 的检查，所以要把它关闭)
        param5 = Parameter('myparam5', nullable=True)
        self.assertEqual(param5.verify(dict(myparam5=None)), None)

    def test_sysrule_nullable(self):
        # nullable 默认应为 False
        param = Parameter('myparam')
        self.assertRaises(VerifyFailed, param.verify, dict(myparam=None))

        # nullable=True 时，各种值都应该能够通过检查
        param2 = Parameter('param2', nullable=True)
        self.assertEqual(param2.verify(dict(param2=None)), None)
        self.assertEqual(param2.verify(dict(param2=1)), 1)

    def test_normal_rule(self):
        class Cust1(Parameter):
            def rule_multiply(self, value):
                return value * self.specs.get('multiply', 2)

            def rule_ten_times(self, value):
                return value * 10

        self.assertEqual(Cust1('param').verify(dict(param=10)), 200)
        self.assertEqual(
            Cust1('param', multiply=3).verify(dict(param=5)), 150)

        # NoValue 和 None 值不会传给普通 rule
        self.assertEqual(
            Cust1('param', required=False).verify({}), NoValue)
        self.assertEqual(
            Cust1('param', nullable=True).verify(dict(param=None)), None)

        class Cust2(Parameter):
            rule_order = ['c', 'e', 'a', 'b', 'd']
            called = []

            def rule_a(self, value):
                self.called.append('a')
                return value

            def rule_b(self, value):
                self.called.append('b')
                return value

            def rule_c(self, value):
                self.called.append('c')
                return value

            def rule_d(self, value):
                self.called.append('d')
                return value

            def rule_e(self, value):
                self.called.append('e')
                return value
        param = Cust2('param')
        param.verify(dict(param=1))
        self.assertEqual(param.called, param.rule_order)


class NoNameParameterTestCase(TestCase):
    def test_define(self):
        param = Parameter()
        self.assertEqual(param.name, NoValue)
        self.assertEqual(param.specs, Parameter.spec_defaults(None))

        param = Parameter(nullable=True)
        self.assertEqual(param.specs, dict(Parameter.spec_defaults(None), nullable=True))

    def test_copy(self):
        param1 = Parameter()

        # noname => noname
        copy1 = param1.copy(nullable=True)
        self.assertEqual(copy1.name, NoValue)
        self.assertEqual(copy1.specs, dict(Parameter.spec_defaults(None), nullable=True))

        # noname => has name
        copy2 = param1.copy('new_name')
        self.assertEqual(copy2.name, 'new_name')

        # has name => no name
        param2 = Parameter('the_param2')
        copy3 = param2.copy(NoValue)
        self.assertEqual(copy3.name, NoValue)

    def test_verify(self):
        param = Parameter()
        self.assertEqual(param.verify(10), 10)
        self.assertRaises(VerifyFailed, param.verify, None)

        param2 = Parameter(nullable=True)
        self.assertEqual(param2.verify(None), None)
