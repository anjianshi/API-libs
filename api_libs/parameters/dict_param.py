from .Parameter import Parameter, VerifyFailed, NoValue
from .utils import ObjectDict

__all__ = ["Dict"]


class Dict(Parameter):
    """Dict("param", type=[
        Str("sub_p1", min_len=1),
        Int("sub_p2", required=False)
    ])
    """
    rule_order = ["format"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        names = set()
        for param in self.specs.get("format"):
            if not isinstance(param, Parameter):
                raise Exception("parameter {}: format 中的内容必须是 Parameter 或其子类， got {}".format(self.name, param))
            if param.name in names:
                raise Exception("parameter {}: format 中不允许出现 name 重复的项({})".format(self.name, param.name))
            names.add(param.name)

    def rule_format(self, value):
        if not isinstance(value, dict):
            raise VerifyFailed("参数 {} 的值必须是 dict (got: {} {})".format(self.name, type(value), value))

        params = self.specs.get("format")

        item_names = set([param.name for param in params])
        unexpected_items = set(value).difference(item_names)
        if len(unexpected_items):
            raise VerifyFailed("不支持以下子项：{}".format(unexpected_items))

        formatted_dict = {}
        for param in params:
            formatted_value = param.verify(value)
            if formatted_value is not NoValue:
                formatted_dict[param.name] = formatted_value
        return ObjectDict(formatted_dict)
