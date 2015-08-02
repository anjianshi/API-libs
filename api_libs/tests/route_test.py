from unittest import TestCase
from ..route import Router, Context, APIRegisterFailed, APICallFailed
from ..parameters import *


class RouterTestCase(TestCase):
    def setUp(self):
        self.router = Router()

    def test_register(self):
        @self.router.register("test.path")
        def fn(context):
            pass
        self.assertTrue(callable(fn))

    def test_register_with_parameters(self):
        @self.router.register("test.path", [Str("arg1")])
        def fn(context, arguments):
            pass
        self.assertTrue(callable(fn))

    def test_illegal_register(self):
        def register(path):
            @self.router.register(path)
            def fn(context):
                pass

        for value in [True, 1, None, "ab/d"]:
            self.assertRaises(APIRegisterFailed, register, value)

    def test_repeat_register(self):
        @self.router.register("test.path")
        def fn(ctx, arg):
            pass

        def register():
            @self.router.register("test.path")
            def fn(ctx, arg):
                pass

        self.assertRaises(APIRegisterFailed, register)

    def test_call(self):
        @self.router.register("test.path", [Str("arg1", default="default_value")])
        def fn(context, arguments):
            return dict(the_result=arguments.arg1)

        self.assertEqual(
            self.router.call("test.path", None, dict(arg1="custom_value")),
            dict(the_result="custom_value"))

        self.assertEqual(
            self.router.call("test.path"),
            dict(the_result="default_value"))

        self.assertRaises(APICallFailed, self.router.call, "test.not_exists_path")

    def test_call_with_no_arguments(self):
        @self.router.register("test.path")
        def fn(context):
            return "some_value"

        self.assertEqual(self.router.call("test.path"), "some_value")

        # 未设置 parameters 的 API 在调用时不允许传入参数值
        self.assertRaises(APICallFailed,
                          self.router.call,
                          "test.path", None, dict(arg1="xyz"))

    def test_context(self):
        @self.router.register("test.path")
        def fn(context):
            return context.data["some_data"]

        self.assertEqual(
            self.router.call("test.path", dict(some_data=100)),
            100)

    def test_context_call(self):
        @self.router.register("test.path.a")
        def fn(context):
            return context.call("test.path.b") * context.data["some_num"]

        @self.router.register("test.path.b")
        def fn2(context):
            return 50 * context.data["some_num"]

        self.assertEqual(
            self.router.call("test.path.a", dict(some_num=10)),
            5000
        )

        self.assertEqual(
            self.router.call("test.path.b", dict(some_num=10)),
            500
        )

    def test_custom_context(self):
        class MyIntContext(Context):
            def __init__(self, router, some_val):
                self.some_int = int(some_val)
                super().__init__(router)

        router = Router(MyIntContext)

        @router.register("test.path")
        def fn(context):
            return context.some_int * 2

        self.assertEqual(
            router.call("test.path", "5"),
            10)

    def test_change_context(self):
        class MyIntContext2(Context):
            def __init__(self, router, some_val):
                self.some_int = int(some_val) * 5

        router = Router()

        @router.register("test.path")
        def fn(context):
            return context.some_int

        router.change_context(MyIntContext2)

        self.assertEqual(
            router.call("test.path", 5),
            25
        )
