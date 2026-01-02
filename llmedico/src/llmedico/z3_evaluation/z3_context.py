from z3 import *


class Z3Context:
    """
    What Z3Context guarantees
    ctx = Z3Context()
    x1 = ctx.bool("x")
    x2 = ctx.bool("x")
    All references to "x" are unified
    Logical meaning is preserved

    use "uninterpreted reference sort" for null/objects
    we declare a new z3 type "Ref"
    it has no logic/ is uninterpreted
    only works for == and !=
    """
    def __init__(self):
        self.vars = {}
        self.ref_sort = DeclareSort("Ref")
        self._refs = {}
        self._null = None

    def bool(self, name: str):
        if name not in self.vars:
            self.vars[name] = Bool(name)
        return self.vars[name]

    def int(self, name: str):
        if name not in self.vars:
            self.vars[name] = Int(name)
        return self.vars[name]

    #to reference objects
    def ref(self, name: str):
        if name not in self._refs:
            self._refs[name] = Const(name, self.ref_sort)
        return self._refs[name]

    #to reference null (our version of null)
    def null(self):
        if self._null is None:
            self._null = Const("null", self.ref_sort)
        return self._null
