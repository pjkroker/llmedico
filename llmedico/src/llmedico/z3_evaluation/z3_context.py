from z3 import *


class Z3Context:
    """
    What Z3Context guarantees
    ctx = Z3Context()
    x1 = ctx.bool("x")
    x2 = ctx.bool("x")
    All references to "x" are unified
    Logical meaning is preserved
    """
    def __init__(self):
        self.vars = {}

    def bool(self, name: str):
        if name not in self.vars:
            self.vars[name] = Bool(name)
        return self.vars[name]

    def int(self, name: str):
        if name not in self.vars:
            self.vars[name] = Int(name)
        return self.vars[name]
