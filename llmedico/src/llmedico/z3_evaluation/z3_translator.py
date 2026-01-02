from z3 import *


from llmedico.z3_evaluation import model_ast
from llmedico.z3_evaluation.model_ast import (
    Expr, And as AstAnd, Or as AstOr, Not as AstNot,
    Var, IntConst, Compare, UnaryMinus, Add, Sub, Mul, BoolConst, Type, Div, Mod as AstMod, expect, NullConst, Method,
)
from llmedico.z3_evaluation.z3_context import Z3Context


class Z3Translator:
    INT_RETURN_METHODS = {
        "size",
        "length",
        "count",
    }

    def __init__(self):
        self.ctx = Z3Context()
        self.var_types: dict[str, model_ast.Type] = {}  # name -> Type.INT | Type.BOOL | Type:REF

    def _expect_var_type(self, var: Var, expected: model_ast.Type):
        name = var.name

        if name not in self.var_types:
            self.var_types[name] = expected
            return

        if self.var_types[name] != expected:
            raise TypeError(
                f"Variable '{name}' used as both "
                f"{self.var_types[name]} and {expected}"
            )

    def translate(self, expr: Expr) -> BoolRef:
        if isinstance(expr, AstAnd):
            for op in (expr.left, expr.right):
                if isinstance(op, Var):
                    self._expect_var_type(op, Type.BOOL)
            return And(self.translate(expr.left), self.translate(expr.right))

        if isinstance(expr, AstOr):
            for op in (expr.left, expr.right):
                if isinstance(op, Var):
                    self._expect_var_type(op, Type.BOOL)
            return Or(self.translate(expr.left), self.translate(expr.right))

        if isinstance(expr, AstNot):
            if isinstance(expr.expr, Var):
                self._expect_var_type(expr.expr, Type.BOOL)
            return Not(self.translate(expr.expr))

        if isinstance(expr, Var):
            t = self.var_types.get(expr.name)
            if t == Type.INT:
                return self.ctx.int(expr.name)
            if t == Type.BOOL:
                return self.ctx.bool(expr.name)
            if t == Type.REF:
                return self.ctx.ref(expr.name)
            t = self.var_types.get(expr.name)
            # if t is None:
            #     raise RuntimeError(f"Uninferred variable: {expr.name}")
            return self.ctx.ref(expr.name) #default: unresolved vars are reference-like objects TODO check if this makes sense

        if isinstance(expr, NullConst):
            return self.ctx.null()

        if isinstance(expr, IntConst): #literal/constant, get directly as z3 obj
            return IntVal(expr.value)

        if isinstance(expr, BoolConst): #literal/constant, get directly as z3 obj
            return BoolVal(expr.value)

        if isinstance(expr, UnaryMinus):
            if isinstance(expr.expr, Var):
                self._expect_var_type(expr.expr, Type.INT)
            return -self.translate(expr.expr) #*-1

        if isinstance(expr, Add):
            expect(expr.left, Type.INT, self)
            expect(expr.right, Type.INT, self)
            return self.translate(expr.left) + self.translate(expr.right)

        if isinstance(expr, Sub):
            expect(expr.left, Type.INT, self)
            expect(expr.right, Type.INT, self)
            return self.translate(expr.left) - self.translate(expr.right)

        if isinstance(expr, Mul):
            expect(expr.left, Type.INT, self)
            expect(expr.right, Type.INT, self)
            return self.translate(expr.left) * self.translate(expr.right)

        if isinstance(expr, Div):
            expect(expr.left, Type.INT, self)
            expect(expr.right, Type.INT,self)

            l = self.translate(expr.left)
            r = self.translate(expr.right)
            return l / r  # Z3 Int division

        if isinstance(expr, AstMod):
            expect(expr.left, Type.INT, self)
            expect(expr.right, Type.INT, self)

            l = self.translate(expr.left)
            r = self.translate(expr.right)

            return l % r #Mod(l, r)

        if isinstance(expr, Method):
            # arguments: infer from context if possible
            for arg in expr.parameters:
                if isinstance(arg, Var):
                    # heuristic: predicate methods usually take refs
                    self._expect_var_type(arg, Type.REF)
            args = [self.translate(a) for a in expr.parameters]

            if expr.receiver is not None and isinstance(expr.receiver, Var):
                self._expect_var_type(expr.receiver, Type.REF)
            # translate receiver if present
            if expr.receiver is not None:
                receiver = self.translate(expr.receiver)
                all_args = [receiver] + args
                arg_sorts = [receiver.sort()] + [a.sort() for a in args]
            else:
                all_args = args
                arg_sorts = [a.sort() for a in args]

            # a.equals(b) OR equals(a, b)
            if expr.name == "equals" and len(all_args) == 2:
                return all_args[0] == all_args[1]

            # x.isEmpty()
            if expr.name == "isEmpty" and len(all_args) == 1:
                f = self.ctx.get_func(
                    "isEmpty",
                    [arg_sorts[0]],
                    BoolSort()
                )
                return f(all_args[0])

            # generic uninterpreted function
            # heuristic: boolean-valued predicates
            if expr.name.startswith("is") or expr.name.startswith("has"):
                ret_sort = BoolSort()
            else:
                ret_sort = self.ctx.ref_sort  # reference-like result

            f = self.ctx.get_func(expr.name, arg_sorts, ret_sort)
            return f(*all_args)

        if isinstance(expr, Compare):
            lt = model_ast.typeof(expr.left)
            rt = model_ast.typeof(expr.right)

            if expr.op in {"==", "!="}:
                # Special-case when null is involved
                if isinstance(expr.left, NullConst) or isinstance(expr.right, NullConst):
                    if isinstance(expr.left, Var):
                        expect(expr.left, Type.REF, self)
                    if isinstance(expr.right, Var):
                        expect(expr.right, Type.REF, self)

                    l = self.translate(expr.left)
                    r = self.translate(expr.right)
                    return l == r if expr.op == "==" else l != r

                # If both sides have known (non-var) types they must match
                if lt is not None and rt is not None and lt != rt:
                    print(lt, rt)
                    raise TypeError("Equality requires operands of same type")

                # If one side has a known type, force the other side to that type (infers vars)
                if lt is not None:
                    expect(expr.right, lt, self)
                if rt is not None:
                    expect(expr.left, rt, self)

                l = self.translate(expr.left)
                r = self.translate(expr.right)

                return l == r if expr.op == "==" else l != r
            else:  # < <= > >=
                expect(expr.left, Type.INT, self)
                expect(expr.right, Type.INT, self)

                l = self.translate(expr.left)
                r = self.translate(expr.right)

                return {
                    "<": l < r,
                    "<=": l <= r,
                    ">": l > r,
                    ">=": l >= r,
                }[expr.op]