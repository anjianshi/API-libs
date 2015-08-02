from .Parameter import Parameter, VerifyFailed

__all__ = ["List"]


class List(Parameter):
    """List("param_name", type=Int(min=1))
    List 的 type specification 所用的 parameter 不需要指定 name。
    """
    rule_order = ["type"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        item_type = self.specs.get("type")
        if not isinstance(item_type, Parameter):
            raise Exception("parameter {}: type specification 的值必须是 Parameter 或其子类, got {}".format(self.name, item_type))

    def rule_type(self, value):
        if type(value) != list:
            raise VerifyFailed("参数 {} 的值必须是 list (got: {} {})".format(self.name, type(value), value))

        item_type = self.specs.get("type")
        formatted_item = []
        for item in value:
            formatted_item.append(item_type.verify(item))
        return formatted_item

    def rule_min_len(self, value):
        """通过 min_len=n 指定 list 的最小长度"""
        if "min_len" in self.specs and len(value) < self.specs["min_len"]:
            raise VerifyFailed("参数 {} 的元素数量不能少于 {} (got: {})".format(
                self.name, self.specs["min_len"], len(value)))
        return value

    def rule_max_len(self, value):
        """通过 max_len=n 指定 list 的最大长度"""
        if "max_len" in self.specs and len(value) > self.specs["max_len"]:
            raise VerifyFailed("参数 {} 的元素数量不能多于 {} (got: {})".format(
                self.name, self.specs["max_len"], len(value)))
        return value
