from z3 import *


from llmedico.z3_evaluation import model_ast
from llmedico.z3_evaluation.model_ast import (
    Expr, And as AstAnd, Or as AstOr, Not as AstNot,
    Var, IntConst, Compare, UnaryMinus, Add, Sub, Mul, BoolConst, Type, Div, Mod as AstMod, expect, NullConst, Method,
    INT_RETURN_METHODS, Conditional, BOOL_RETURN_METHODS, MATCH_METHODS, LambdaExpr, InstanceOf,
)
from llmedico.z3_evaluation.z3_context import Z3Context


class Z3Translator:


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
                f"{self.var_types[name]} and {expected}")

    def _infer_lambda_param_type(self, body: Expr) -> Type | None:
        """
        Infer the type of a lambda parameter from its body.
        Currently supports INT inference only.
        """
        if isinstance(body, Compare):
            if body.op in {"<", "<=", ">", ">="}:
                return Type.INT

        if isinstance(body, (Add, Sub, Mul, Div, AstMod)):
            return Type.INT

        # recurse if needed
        if isinstance(body, (AstAnd, AstOr)):
            return self._infer_lambda_param_type(body.left) or \
                self._infer_lambda_param_type(body.right)

        if isinstance(body, AstNot):
            return self._infer_lambda_param_type(body.expr)

        return None

    def translate(self, expr: Expr, return_type: model_ast=None) -> BoolRef:
        if return_type is not None: # set return type once before entering recursive translation
            self._expect_var_type(Var("methodResultID"), return_type)
        return self._translate(expr)

    def _translate(self, expr: Expr) -> BoolRef:
        if isinstance(expr, AstAnd):
            for op in (expr.left, expr.right):
                if isinstance(op, Var):
                    self._expect_var_type(op, Type.BOOL)
            return And(self._translate(expr.left), self._translate(expr.right))

        if isinstance(expr, AstOr):
            for op in (expr.left, expr.right):
                if isinstance(op, Var):
                    self._expect_var_type(op, Type.BOOL)
            return Or(self._translate(expr.left), self._translate(expr.right))

        if isinstance(expr, AstNot):
            if isinstance(expr.expr, Var):
                self._expect_var_type(expr.expr, Type.BOOL)
            return Not(self._translate(expr.expr))

        if isinstance(expr, Var):
            #for lambda
            bound = self.ctx.lookup(expr.name)
            if bound is not None:
                return bound

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
            return self.ctx.ref(expr.name) #default: unresolved vars are reference-like objects

        if isinstance(expr, NullConst):
            return self.ctx.null()

        if isinstance(expr, IntConst): #literal/constant, get directly as z3 obj
            return IntVal(expr.value)

        if isinstance(expr, BoolConst): #literal/constant, get directly as z3 obj
            return BoolVal(expr.value)

        if isinstance(expr, UnaryMinus):
            if isinstance(expr.expr, Var):
                self._expect_var_type(expr.expr, Type.INT)
            return -self._translate(expr.expr) #*-1

        if isinstance(expr, Add):
            expect(expr.left, Type.INT, self)
            expect(expr.right, Type.INT, self)
            return self._translate(expr.left) + self._translate(expr.right)

        if isinstance(expr, Sub):
            expect(expr.left, Type.INT, self)
            expect(expr.right, Type.INT, self)
            return self._translate(expr.left) - self._translate(expr.right)

        if isinstance(expr, Mul):
            expect(expr.left, Type.INT, self)
            expect(expr.right, Type.INT, self)
            return self._translate(expr.left) * self._translate(expr.right)

        if isinstance(expr, Div):
            expect(expr.left, Type.INT, self)
            expect(expr.right, Type.INT,self)

            l = self._translate(expr.left)
            r = self._translate(expr.right)
            return l / r  # Z3 Int division

        if isinstance(expr, AstMod):
            expect(expr.left, Type.INT, self)
            expect(expr.right, Type.INT, self)

            l = self._translate(expr.left)
            r = self._translate(expr.right)

            return l % r #Mod(l, r)

        if isinstance(expr, Method):
            #for lambda
            if expr.name == "stream" and len(expr.parameters) == 0:
                return self._translate(expr.receiver)
            # anyMatch / allMatch / noneMatch
            if expr.name in MATCH_METHODS:
                if len(expr.parameters) != 1 or not isinstance(expr.parameters[0], LambdaExpr):
                    raise TypeError(f"{expr.name} expects a single lambda")

                collection = self._translate(expr.receiver)
                lam: LambdaExpr = expr.parameters[0]

                # fresh index variable
                i = self.ctx.fresh_int("i")

                # infer lambda parameter type
                param_type = self._infer_lambda_param_type(lam.body)

                # choose element sort accordingly
                if param_type == Type.INT:
                    elem = self.ctx.select_int(collection, i)
                else:
                    elem = self.ctx.select(collection, i)

                self.ctx.push_env()
                self.ctx.bind(lam.param, elem)
                predicate = self._translate(lam.body)
                self.ctx.pop_env()

                length = self.ctx.length(collection)
                in_bounds = And(i >= 0, i < length)

                if expr.name == "anyMatch":
                    return Exists([i], And(in_bounds, predicate))

                if expr.name == "allMatch":
                    return ForAll([i], Implies(in_bounds, predicate))

                if expr.name == "noneMatch":
                    return Not(Exists([i], And(in_bounds, predicate)))

            #regular Methods
            # arguments: infer from context if possible
            for arg in expr.parameters:
                if isinstance(arg, Var):
                    # heuristic: predicate methods usually take refs
                    self._expect_var_type(arg, Type.REF)
            args = [self._translate(a) for a in expr.parameters]

            if expr.receiver is not None and isinstance(expr.receiver, Var):
                self._expect_var_type(expr.receiver, Type.REF)
            # translate receiver if present
            if expr.receiver is not None:
                receiver = self._translate(expr.receiver)
                all_args = [receiver] + args
                arg_sorts = [receiver.sort()] + [a.sort() for a in args]
            else:
                all_args = args
                arg_sorts = [a.sort() for a in args]

            # return type handling
            # numeric-returning methods (e.g. size(x))

            if model_ast.is_int(expr.name):
                # arguments must be references
                for arg in expr.parameters:
                    if isinstance(arg, Var):
                        self._expect_var_type(arg, Type.REF)

                ret_sort = IntSort()

            # boolean predicates
            elif expr.name == "equals":
                return all_args[0] == all_args[1]

            elif expr.name == "isEmpty" and len(all_args) == 1:
                f = self.ctx.get_func(
                    "isEmpty",
                    [arg_sorts[0]],
                    BoolSort()
                )
                return f(all_args[0])

            elif model_ast.is_bool(expr.name) or \
                    expr.name.startswith("is") or \
                    expr.name.startswith("has"):
                ret_sort = BoolSort()

            # default: opaque object-valued method
            else:
                ret_sort = self.ctx.ref_sort

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

                    l = self._translate(expr.left)
                    r = self._translate(expr.right)
                    return l == r if expr.op == "==" else l != r

                # If both sides have known (non-var) types they must match
                if lt is not None and rt is not None and lt != rt:
                    raise TypeError("Equality requires operands of same type")

                # If one side has a known type, force the other side to that type (infers vars)
                if lt is not None:
                    expect(expr.right, lt, self)
                if rt is not None:
                    expect(expr.left, rt, self)

                l = self._translate(expr.left)
                r = self._translate(expr.right)

                return l == r if expr.op == "==" else l != r
            else:  # < <= > >=
                expect(expr.left, Type.INT, self)
                expect(expr.right, Type.INT, self)

                l = self._translate(expr.left)
                r = self._translate(expr.right)

                return {
                    "<": l < r,
                    "<=": l <= r,
                    ">": l > r,
                    ">=": l >= r,
                }[expr.op]

        if isinstance(expr, Conditional):
            expect(expr.cond, Type.BOOL, self)

            t_then = model_ast.typeof(expr.then)
            t_else = model_ast.typeof(expr.otherwise)

            if t_then is not None:
                expect(expr.otherwise, t_then, self)
            if t_else is not None:
                expect(expr.then, t_else, self)

            c = self._translate(expr.cond)
            t = self._translate(expr.then)
            e = self._translate(expr.otherwise)

            return If(c, t, e)

        if isinstance(expr, InstanceOf):
            expect(expr.expr, Type.REF, self)
            obj = self._translate(expr.expr)

            f = self.ctx.get_func(
                f"instanceof_{expr.type_name.replace('.', '_')}",
                [obj.sort()],
                BoolSort()
            )
            return f(obj)

