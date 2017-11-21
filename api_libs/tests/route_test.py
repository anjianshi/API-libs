from unittest import TestCase
from ..route import Router, Context, RouteRegisterFailed, RouteCallFailed
from ..parameters import Str
from ..interface import interface


class RouterTestCase(TestCase):
    def setUp(self):
        self.router = Router()

    def test_register(self):
        @self.router.register('test.path')
        def fn(context):
            pass
        self.assertTrue(callable(fn))

    def test_register_with_parameters(self):
        @self.router.register('test.path', [Str('arg1')])
        def fn(context, args):
            pass
        self.assertTrue(callable(fn))

    def test_register_with_interface(self):
        @self.router.register('test.path')
        @interface([Str('arg1')])
        def fn(context, args):
            return args.arg1
        self.assertEqual(
            self.router.call('test.path', None, dict(arg1='hello')),
            'hello'
        )

    def test_illegal_register(self):
        def register(path):
            @self.router.register(path)
            def fn(context):
                pass

        for value in [True, 1, None, 'ab/d']:
            self.assertRaises(RouteRegisterFailed, register, value)

    def test_repeat_register(self):
        @self.router.register('test.path')
        def fn(ctx):
            pass

        def register():
            @self.router.register('test.path')
            def fn(ctx):
                pass

        self.assertRaises(RouteRegisterFailed, register)

    def test_case_insensitive_register(self):
        @self.router.register('TestPath')
        def fn(ctx):
            pass

        def register():
            @self.router.register('testpath')
            def fn(ctx):
                pass

        self.assertRaises(RouteRegisterFailed, register)

    def test_call(self):
        @self.router.register('test.path', [Str('arg1', default='default-value')])
        def fn(context, args):
            return dict(the_result=args.arg1)

        self.assertEqual(
            self.router.call('test.path', None, dict(arg1='custom-value')),
            dict(the_result='custom-value'))

        self.assertEqual(
            self.router.call('test.path'),
            dict(the_result='default-value'))

        self.assertRaises(RouteCallFailed, self.router.call, 'test.not_exists_path')
        self.assertRaises(RouteCallFailed, self.router.call, 123)

    def test_case_insensitive_call(self):
        @self.router.register('TestPath')
        def fn(context):
            return 'value'

        self.assertEqual(self.router.call('TestPath'), 'value')
        self.assertEqual(self.router.call('testpath'), 'value')
        self.assertEqual(self.router.call('testPath'), 'value')

    def test_call_with_no_arguments(self):
        @self.router.register('test.path')
        def fn(context):
            return 'some_value'
        self.assertEqual(self.router.call('test.path'), 'some_value')

    def test_context(self):
        @self.router.register('test.path')
        def fn(context):
            return context.data['some_data']

        self.assertEqual(
            self.router.call('test.path', dict(some_data=100)),
            100)

        context_instance = self.router.context_cls(self.router, dict(some_data=100))
        self.assertEqual(
            self.router.call('test.path', context_instance),
            100)

    def test_context_call(self):
        @self.router.register('test.path.a')
        def fn(context):
            return context.call('test.path.b') * context.data['some_num']

        @self.router.register('test.path.b')
        def fn2(context):
            return 50 * context.data['some_num']

        self.assertEqual(
            self.router.call('test.path.a', dict(some_num=10)),
            5000
        )

        self.assertEqual(
            self.router.call('test.path.b', dict(some_num=10)),
            500
        )

    def test_custom_context(self):
        class MyIntContext(Context):
            def __init__(self, router, some_val):
                self.some_int = int(some_val)
                super().__init__(router)

        router = Router(MyIntContext)

        @router.register('test.path')
        def fn(context):
            return context.some_int * 2

        self.assertEqual(
            router.call('test.path', '5'),
            10)

    def test_change_context(self):
        class MyIntContext2(Context):
            def __init__(self, router, some_val):
                self.some_int = int(some_val) * 5

        router = Router()

        @router.register('test.path')
        def fn(context):
            return context.some_int

        router.change_context(MyIntContext2)

        self.assertEqual(
            router.call('test.path', 5),
            25
        )
