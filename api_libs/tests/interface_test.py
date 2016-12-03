from unittest import TestCase
from ..interface import interface, bound_interface, InterfaceCallFailed
from ..parameters import Str


class InterfaceTestCase(TestCase):
    def test_define_with_no_parameters(self):
        @interface()
        def fn():
            return 123
        self.assertEqual(fn(), 123)

        # 未定义参数列表的 interface function，不能带有 args 参数
        @interface()
        def fn2(args):
            return 123
        self.assertRaises(TypeError, lambda: fn2())

        # 未定义参数列表的 interface，调用时不允许传入参数值
        self.assertRaises(InterfaceCallFailed, lambda: fn(dict(a=1)))

    def test_define_with_parameters(self):
        @interface([Str("arg1")])
        def fn(args):
            return args.arg1
        self.assertEqual(fn(dict(arg1="Hello")), "Hello")

        # 定义了参数列表的 interface function 必须接收一个名为 args 参数
        @interface([Str("arg1")])
        def fn():
            return "content"
        self.assertRaises(TypeError, lambda: fn(dict(arg1="hello")))

    def test_define_with_classmethod(self):
        class Cls:
            @classmethod
            @interface()
            def fn1(cls):
                return cls

            @classmethod
            @bound_interface()
            def fn2(cls):
                return cls

        self.assertRaises(InterfaceCallFailed, Cls.fn1)
        self.assertEqual(Cls.fn2(), Cls)

    def test_define_with_instance_method(self):
        class Cls:
            @interface()
            def fn1(self):
                return self

            @bound_interface()
            def fn2(self):
                return self

        o = Cls()

        self.assertRaises(InterfaceCallFailed, o.fn1)
        self.assertEqual(o.fn2(), o)
