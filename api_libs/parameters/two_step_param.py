from .Parameter import Parameter, VerifyFailed, NoValue

__all__ = ["CanHas", "CanNotHas"]

"""
这两个 Parameter 用于参数值两段检查。

API-libs 默认会在 API handler 被实际调用前，先对参数进行验证、格式化。
但有时对参数的实际要求会因各种环境因素而改变。
例如参数 A 的值为 1 的时候，参数 B 的类型应该是 int；但参数 A 的值为 2 的时候，参数 B 的类型应该为 str。
这种情况下，就有必要在 API handler 内部再进行一次检查。
系统自动检查时，不处理参数 B，直接放行；待进入 handler 内部后，再根据取到的参数 A 的值对参数 B 进行实际的验证（通过 Arguments.future_build() 方法）。
"""


class CanHas(Parameter):
    """允许客户端为此 parameter 赋值，但不进行任何检查，包括 required。
    一般用于在二段验证的第一段（系统自动进行的那一段）对某个参数无条件放行"""

    # 把此属性清空，使得所有 sysrule 都不被执行，也就是无条件放行
    sysrule_order = []


class CanNotHas(Parameter):
    """不允许客户端为此 parameter 赋值。
    一般用于二段验证的第二段（handler 中手动运行的那段）。把第一段中放行进来、但现在根据情况认为不应该被赋值的参数屏蔽掉。"""

    # 移除所有 sysrule，用自定义的一个代替
    # 之所以要定义一个 sysrule，是因为普通 rule 接触不到 None 值，没法对其进行屏蔽
    sysrule_order = ["verify"]

    def sysrule_verify(self, value):
        if value is not NoValue:
            raise VerifyFailed("此字段 name={} 不应被赋值".format(self.name))
        return NoValue
