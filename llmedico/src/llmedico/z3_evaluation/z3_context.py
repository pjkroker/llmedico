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
        self.funcs = {}
        self.env_stack: list[dict[str, ExprRef]] = [{}]
        self._fresh_counter = 0

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

    def get_func(self, name, arg_sorts, ret_sort):
        key = (name, tuple(arg_sorts), ret_sort)
        if key not in self.funcs:
            self.funcs[key] = Function(name, *arg_sorts, ret_sort)
        return self.funcs[key]

    #to support lambda ->
    def push_env(self):
        self.env_stack.append({})

    def pop_env(self):
        self.env_stack.pop()

    def bind(self, name: str, value: ExprRef):
        self.env_stack[-1][name] = value

    def lookup(self, name: str):
        for env in reversed(self.env_stack):
            if name in env:
                return env[name]
        return None

    def length(self, collection):
        return self.get_func("length", [collection.sort()], IntSort())(collection)

    def select(self, collection, idx):
        return self.get_func("select", [collection.sort(), IntSort()], self.ref_sort)(
            collection, idx
        )

    def fresh_int(self, prefix: str = "i"):
        self._fresh_counter += 1
        return Int(f"{prefix}_{self._fresh_counter}")

    def select_int(self, collection, idx):
        return self.get_func("select_int",[collection.sort(), IntSort()],IntSort())(collection, idx)

