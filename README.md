API-libs: 一套灵活的组件，帮助你快速搭建起一个 API 系统

Python 3.4 only

## API 系统的结构
- `router`        通过它来注册、调用 API handler

- `handler`       由用户注册在 router 中的一个个函数，通过它们来实现业务逻辑

- `paramemter`    每个 handler 都有自己的参数列表，里面可以指定各参数的名称、类型、以及格式要求。
                调用 handler 时，会根据它，对调用者传入的参数值进行检查/格式化。

- `context`       context 中存放着与此次 API 调用相关的上下文信息，还会提供一些辅助方法，帮助 handler 更容易地完成任务。
                context 有很多种类型，每种类型提供不同的信息和方法，适用于不同的任务。每个 router 都会绑定一种 context 类型。
                另外，在调用 API handler 时，除了要传入参数值，还要传入 context 初始化所需的数据。

- `adapter`       router 本身不响应 HTTP 请求。如果想把 API 以 Web 服务的形式提供出来，就需要用到 adapter。
                它可以把 HTTP 请求转换为 API 调用，再把调用结果以 JSON 的形式输出给客户端。
                目前 API-libs 只提供基于 Tornado 的 adapter。

## 安装
```bash
pip install api_libs
```

## 测试
```bash
nosetests
```

                
## Example

### 基本用法
```python
from api_libs import Router

router = Router()


@router.register("get_name")
def fn(context):
    return "David"

router.call("get_name")  # return "David"
```

### 给 API handler 定义参数
详见后面的 `参数定义` 小节
```python
from api_libs import Router
from api_libs.parameters import *

router = Router()

@router.register("math.divide", [Int("a"), Int("b", nozero=True)])
def divide(context, arguments):
    # arguments 既可以以 object 的形式，也可以以 dict 的形式访问
    return arguments.a / arguments["b"]

# 第二个参数是传给 context 的，这里我们并没有用到 context data，所以传入 None
router.call("math.divide", None, dict(a=10, b=5))   # return 2
router.call("math.divide", None, dict(a=10, b=0))   # 参数 b 不符合 nozero 的要求，报错
```

### 使用复合型参数(List, Dict)
```python
users = {
    # category: [user_names]
}


@router.register("users.add", [
    Str("category"), 
    # 至少提供一个 user_name；每个 user_name 至少为 3 个字符
    # notice: 指定 List 的 type 时，不用给 parameter 设置 name
    List("user_names", type=Str(min_len=3), min_len=1)
])
def add_users(context, arguments):
    users[arguments.category] = arguments.user_names
    return users

router.call("users.add", None, dict(category="home", user_names=["David", "Tom"]))
# return {"home": ["David", "Tom"]}


users_v2 = {
    # category: [ {user1_profile}, {user2_profile},  ]
}


@router.register("users.add.v2", [
    Str("category"),
    List("profiles", type=Dict(
        format=[
            Str("name"),
            Int("age"),
            Str("address", required=False),
        ]
    ))
])
def add_users_v2(context, arguments):
    users_v2[arguments.category] = arguments.profiles
    return users_v2

router.call("users.add", None, dict(category="home", profiles=[
    dict(name="David", age=18, address="Tokyo"),
    dict(name="Tom", age=20),
]))
# return {"home": [{"name": "David", "age": 18, address: "Tokyo"}, {"name": "Tom", "age": 20}]}
```

### 两步验证参数
```python
@router.register("customer.register", [
    Int("type"),  # 1 代表个人, 2 代表公司,
    CanHas("personal_name"),
    CanHas("compony_name"),
    Str("mobile")
])
def fn(context, arguments):
    if arguments.type == 1:
        arguments.future_build([Str("personal_name", max_len=15), CanNotHas("company_name")])
        return dict(personal=arguments.personal_name, mobile=arguments.mobile)
    else:
        arguments.future_build([Str("company_name", max_len=30), CanNotHas("personal_name")])
        return dict(compony=arguments.compony_name, mobile=arguments.mobile)

router.call("customer.register", None, dict(
    type=1,
    personal_name="David",
    mobile="123343"
))
# return dict(personal="David", mobile="123343")
```


### 在一个 API handler 中调用其他 handler
```python
class Player:
    def __init__():
        self.money = 1000
        self.props = ["sword"]

players = {
    "David": Player(),
    "Tom": Player()
}


@router.register("props.buy", [Str("player"), Str("props_name")])
def fn1(context, arguments):
    player = players[arguments.player]
    consume_result = router.call("player.consume", None, dict(player=arguments.player, money=100))
    if consume_result:
        player.props.append(arguments.props_name)
        return True
    else:
        return False


@router.register("player.consume", [Str("player"), Int("money", min=1)])
def fn2(context, arguments):
    player = players[arguments.player]
    if player.money > arguments.money:
        player.money -= arguments.money
        return True
    else:
        return False

router.call("props.buy", None, dict(player="Tom", props_name="boots"))  # return True
```

### 使用 context
```python
class Player:
    def __init__():
        self.money = 1000
        self.props = ["sword"]

players = {
    "David": Player(),
    "Tom": Player()
}


@router.register("props.buy", [Str("props_name")])
def fn1(context, arguments):
    # 这里改为通过 context 来提供 player 信息
    player = context.data["player"]
    # 使用 context.call() 而不是 router.call()，这样当前的 context 信息就能被传递给下一个 API
    consume_result = context.call("player.consume", dict(money=100))
    if consume_result:
        player.props.append(arguments.props_name)
        return True
    else:
        return False


@router.register("player.consume", [Int("money", min=1)])
def fn2(context, arguments):
    player = context.data["player"]
    if player.money > arguments.money:
        player.money -= arguments.money
        return True
    else:
        return False

router.call("props.buy", dict(player=player["Tom"]), dict(props_name="boots"))  # return True
```

### 使用自定义的 Context 类型
上面的例子用的是默认的 Context，它提供的功能很有限。实际上通过 context 可以做非常多的事情。
我们可以根据需要，自己定义一个 Context 类型，传给 Router。

```python
from api_libs import Router, Context
from api_libs.parameters import *


class Player:
    def __init__():
        self.money = 1000
        self.props = ["sword"]

players = {
    "David": Player(),
    "Tom": Player()
}


class PlayerContext(Context):
    def __init__(self, router, player_name):
        super().__init__(router)
        self.player = players[player_name]

router = Router(PlayerContext)


@router.register("player.consume", [Int("money", min=1)])
def fn2(context, arguments):
    # router 绑定了我们自定义的 context，因此不用再访问 context.data["player"]，而是直接用 context.player
    if context.player.money > arguments.money:
        context.player.money -= arguments.money
        return True
    else:
        return False

# 传递 context 初始化信息的步骤也得到了简化
router.call("player.consume", "Tom", dict(money=100))   # return True
```

### 使用 Tornado Adapter
```python
from API-libs.adapters.tornado_adapter import TornadoAdapter
from tornado.web import Application

# 实例化 adapter
adapter = TornadoAdapter()

# 把 API 注册在 adapter 下属的 api router 中
# 这样这个 API 才能被客户端所调用
@adapter.api_router.register("a.b.c")
def fn(context):
    return dict(result=True)

# 把 adapter 提供的 RequestHandler 放入 tornado application
application = Application([
    ("/api/(.+)", adapter.RequestHandler),
])
application.listen(8888)
tornado.ioloop.IOLoop.current().start()

# GET /api/a.b.c  => Response: {"result": true}
```


## 参数(parameter)定义
Example: `Int("myint", min=1, nozero=True)`

系统提供了以下类型的 parameter：
- `Int`，要求传递进来的参数值必须是 int 类型
- `Decimal`，要求参数值是 int 或 float
- `Str`，要求参数值是 str
- `Bool` 要求参数值是 True 或 False
- `Datetime`，要求参数值是合法的 timestamp (int / float)，最终会返回一个 python datetime.datetime 对象
- `Date`，和 Datetime 一样，不过返回的是 datetime.date 对象
- `List`，要求参数值是指定类型的一组数据
- `Dict`，要求参数值是 dict，且符合 format spec 中定义的格式
- `CanHas`，对参数无条件放行，无论赋值与否、赋了什么值，都能通过验证。参见上面的“两步验证参数”部分
- `CanNotHas`，无条件屏蔽此参数，只要赋了值（包括 None 值）就会报错。参见上面的“两步验证参数”部分

构建 Parameter 时，可以指定一些选项(specification)。

### 大部分 Parameter 通用的选项
- `default`         给参数设置默认值
- `required=True`   若为 True，则此参数必须被赋值（但是不关心它是什么值，即使是 None 也无所谓）。
                    在设置了 `default` 的情况下，参数总是能通过 `required` 的检查。
- `nullable=False`  是否允许此参数的值为 None

### Int、Decimal 独有的选项
- `min`          此参数允许的最小数值
- `max`          此参数允许的最大数值
- `nozero=False` 是否允许参数值为 0

### Str 独有的选项
- `trim=True`   是否清除参数值两侧的空白符
- `min_len`     字符串最小长度
- `max_len`     字符串最大长度
- `regex`       要求参数值能与这里给出的正则表达式匹配
- `not_regex`   要求参数值不能与这里给出的正则表达式匹配（可用于剔除一些非法字符）

### List 独有的选项
- `min_len`     list 的最小长度
- `max_len`     list 的最大长度
