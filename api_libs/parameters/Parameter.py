import inspect


class _NoValueCls:
    def __repr__(self):
        return 'Parameter.NoValue'
NoValue = _NoValueCls()


class VerifyFailed(Exception):
    pass


class Parameter:
    """
    定义一个 API 参数。

    :arg string name: 参数名
    :arg specs: 对这个参数的要求（specification）。例如：required=True, nullable=False, max=10
      specs 需要以 kwargs 的形式提供，key 部分是规则名，value 部分是具体的要求。

    Parameter 与它的各个子类中，都定义了一系列 rule 函数，系统会按照一定顺序调用它们，来完成对参数值的检查和格式化。
    rule 函数在接收到参数值后，可以有如下几种行为：
        1. 返回任意值，代表参数通过验证，并把参数值设为这个返回值
        2. 抛出 VerifyFailed 代表验证失败，抛出的时候可以附带一个失败说明
    通过 specs，可以设定这些 rule 的检查规则。

    rule 分两种：
    一种是在 Parameter 基类中已定义好的核心 rule，称之为 sysrule；
    另一种是在每个 Parameter 的子类中定义的 rule，称之为普通 rule。

    sysrule 的方法名以 ``sysrule_`` 开头；普通 rule 则以 ``rule_`` 开头。
    sysrule 会比普通 rule 先执行。
    sysrule 之间的执行顺序通过 sysrule_order 指定，这个顺序是设计好的，一般不需要修改。
    普通 rule 之间的执行顺序通过 rule_order 指定。没出现在这个列表中的 rule 会在列表中的 rule 都调用完后，以随机的顺序被调用。

    如果当前参数没有被赋值，那么会把 NoValue 传给 rule （没赋值和赋值为 None 完全是两回事，千万不要搞混）。
    Parameter 默认只让 sysrule 处理 NoValue 和 None 值，如果 sysrule 都执行完毕后，参数值仍然是 NoValue 或 None，那么整个检查行为到此结束，
    把 NoValue / None 作为最终的结果，后面的普通 rule 不再被执行。
    这样设计使得普通 rule 里就不用包含处理 NoValue 和 None 的代码了，节省了精力。因为普通的 rule 不太可能会为 NoValue 和 None 准备什么处理逻辑，即使碰到了也顶多是跳过执行而已。

    ----------

    default specs: required=True, nullable=False
    """
    def __init__(self, name, **specs):
        self.name = name
        self.specs = specs
        self._normal_rules = self.sorted_normal_rules()

    def sorted_normal_rules(self):
        if len(self.rule_order) != len(set(self.rule_order)):
            raise Exception("rule_order 不允许出现重复的内容({})".format(self.rule_order))

        methods = inspect.getmembers(self, predicate=inspect.ismethod)
        normal_rules = [name[5:] for name, _ in methods if name[:5] == "rule_"]

        return self.rule_order + list(
            set(normal_rules).difference(set(self.rule_order)))

    def copy(self, name=None, remove=[], inplace={}):
        """以当前 Parameter 为基础，复制出一个新的 Parameter

        :arg string name: 新 parameter 的名称。若不指定，则沿用原来的名称。
        :arg string[] remove: 在新 parameter 中剔除指定的 rule_spec。
        :arg dict inplace: 在新 parameter 中修改原来某些 rule_spec 的值，或是插入一些原来没有的 spec

            p1 = Parameter("p1", required=True, default=1)
            p2 = p1.copy("p2", remove=["required"], inplace=dict(default=2, nullable=True))
            # 相当于： Parameter("p2", default=2, nullable=True)
        """
        if name is None:
            name = self.name

        specs = self.specs.copy()
        for key in remove:
            specs.pop(key)
        for key, value in inplace.items():
            specs[key] = value

        return type(self)(name, **specs)

    def verify(self, arguments):
        value = arguments.get(self.name, NoValue)

        for rule_name in self.sysrule_order:
            value = getattr(self, "sysrule_" + rule_name)(value)

        if value is not NoValue and value is not None:
            for rule_name in self._normal_rules:
                value = getattr(self, "rule_" + rule_name)(value)

        return value

    # 各 sysrule 的执行顺序
    sysrule_order = ["default", "required", "nullable"]
    # 各普通 rule 的执行顺序
    rule_order = []

    def sysrule_default(self, value):
        """如果某个参数没有被赋值，则给予其一个默认值"""
        if value is NoValue and "default" in self.specs:
            value = self.specs["default"]
        return value

    def sysrule_required(self, value):
        """若为 true，则参数必须被赋值（但是不关心它是什么值，即使是 None 也无所谓）"""
        if self.specs.get("required", True) and value is NoValue:
            raise VerifyFailed("缺少必要参数：{}".format(self.name))
        return value

    def sysrule_nullable(self, value):
        """是否允许参数值为 None。
        没被赋值的参数它的值自然不是 None，所以可以通过这个 rule 的检查"""
        if not self.specs.get("nullable", False) and value is None:
            raise VerifyFailed("参数 {} 不允许为 None".format(self.name))
        return value
