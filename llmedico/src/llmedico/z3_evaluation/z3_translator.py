from z3 import *

from llmedico.z3_evaluation import model_ast
from llmedico.z3_evaluation.model_ast import (
    Expr, And as AstAnd, Or as AstOr, Not as AstNot,
    Var, IntConst, Compare, UnaryMinus, Add, Sub, Mul, BoolConst, Type
)
from llmedico.z3_evaluation.z3_context import Z3Context


class Z3Translator:

    def __init__(self):
        self.ctx = Z3Context()
        self.var_types: dict[str, model_ast.Type] = {}  # name -> Type.INT | Type.BOOL

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
            t = self.var_types.get(expr.name, Type.BOOL)
            if t == Type.INT:
                return self.ctx.int(expr.name)
            return self.ctx.bool(expr.name)

        if isinstance(expr, IntConst): #literal/constant, get directly as z3 obj
            return IntVal(expr.value)

        if isinstance(expr, BoolConst): #literal/constant, get directly as z3 obj
            return BoolVal(expr.value)

        if isinstance(expr, UnaryMinus):
            if isinstance(expr.expr, Var):
                self._expect_var_type(expr.expr, Type.INT)
            return -self.translate(expr.expr) #*-1

        if isinstance(expr, Add):
            for op in (expr.left, expr.right):
                if isinstance(op, Var):
                    self._expect_var_type(op, Type.INT)
            return self.translate(expr.left) + self.translate(expr.right)

        if isinstance(expr, Sub):
            for op in (expr.left, expr.right):
                if isinstance(op, Var):
                    self._expect_var_type(op, Type.INT)
            return self.translate(expr.left) - self.translate(expr.right)

        if isinstance(expr, Mul):
            for op in (expr.left, expr.right):
                if isinstance(op, Var):
                    self._expect_var_type(op, Type.INT)
            return self.translate(expr.left) * self.translate(expr.right)

        if isinstance(expr, Compare):
            lt = model_ast.typeof(expr.left)
            rt = model_ast.typeof(expr.right)

            if expr.op in {"==", "!="}:
                if lt is not None and rt is not None and lt != rt:
                    raise TypeError("Equality requires operands of same type")

                # infer variable types from the other side
                if isinstance(expr.left, Var) and rt is not None:
                    self._expect_var_type(expr.left, rt)

                if isinstance(expr.right, Var) and lt is not None:
                    self._expect_var_type(expr.right, lt)

                l = self.translate(expr.left)
                r = self.translate(expr.right)

                return l == r if expr.op == "==" else l != r

            else:  # < <= > >=
                for side in (expr.left, expr.right): # both need to be INT
                    if isinstance(side, Var):
                        self._expect_var_type(side, Type.INT)

                l = self.translate(expr.left)
                r = self.translate(expr.right)

                return {
                    "<": l < r,
                    "<=": l <= r,
                    ">": l > r,
                    ">=": l >= r,
                }[expr.op]