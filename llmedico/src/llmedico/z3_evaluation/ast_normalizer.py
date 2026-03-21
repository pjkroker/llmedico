from _ast import Constant

from llmedico.z3_evaluation.model_ast import *
import logging

logger = logging.getLogger(__name__)

class UnsupportedAssertion(Exception):
    pass

class AstNormalizer:

    BOOL_EXPR = (BoolConst,
            BoolVar,
            Compare,
            And,
            Or,
            Not,
            InstanceOf)

    def _is_boolean_expr(self, expr: Expr) -> bool:
        return isinstance(expr, self.BOOL_EXPR)

    def _is_java_util_arrays_stream(self, expr: Method) -> bool:
        return (
                isinstance(expr, Method)
                and expr.name == "stream"
                and len(expr.parameters) == 1
                and isinstance(expr.receiver, Method)
                and expr.receiver.name == "Arrays"
                and isinstance(expr.receiver.receiver, Method)
                and expr.receiver.receiver.name == "util"
                and isinstance(expr.receiver.receiver.receiver, Var)
                and expr.receiver.receiver.receiver.name == "java"
        )

    def normalize_expr(self, expr: Expr) -> Optional[Expr]:

        # ---- Method calls ----
        if isinstance(expr, Method):

            # NEW: collapse java.util.Arrays.stream(x) → stream(x)
            if self._is_java_util_arrays_stream(expr):
                arg = self.normalize_expr(expr.parameters[0])
                normalized = Method(receiver=None, name="stream", parameters=[arg])
                logger.warning(
                    f"Normalized java.util.Arrays.stream()\n"
                    f"before: {expr}\n"
                    f"after:  {normalized}"
                )
                return normalized

            # keep this ONLY if other code relies on it
            # (otherwise it can now be removed safely)
            # if expr.name == "Arrays" and isinstance(expr.receiver, Method) and expr.parameters == []:
            #     return self.normalize_expr(expr.receiver)

            # # returning None is dangerous, but left intact per your request
            # if expr.name == "util" and isinstance(expr.receiver, Var) and expr.receiver.name == "java":
            #     return None

            # ---- stream normalization ----
            if expr.name == "stream":
                receiver = self.normalize_expr(expr.receiver) if expr.receiver else None
                parameters = [self.normalize_expr(p) for p in expr.parameters]

                # stream(x) → x.stream()
                if receiver is None and len(parameters) == 1:
                    normalized = Method(receiver=parameters[0], name="stream", parameters=[])
                    logger.warning(
                        f"Normalized stream call\n"
                        f"before: {expr}\n"
                        f"after:  {normalized}"
                    )
                    return normalized

                # keep method form if already instance-based
                if receiver is not None:
                    return Method(receiver=receiver, name="stream", parameters=parameters)

            # ---- method chaining ----
            elif isinstance(expr.receiver, Method):
                normalized_receiver = self.normalize_expr(expr.receiver)

                rebuilt = Method(
                    receiver=normalized_receiver,
                    name=expr.name,
                    parameters=[self.normalize_expr(p) for p in expr.parameters]
                )

                #recursion guard
                if rebuilt == expr:
                    return rebuilt

                return self.normalize_expr(rebuilt)

            return expr

        if isinstance(expr, BitWiseShift):
            norm_shift = Method(receiver=None, name=expr.op, parameters=[expr.left, expr.right])
            logger.critical(f"Normalized {expr} to canonical uninterpreted {norm_shift}")
            return norm_shift

        if isinstance(expr, InstanceOf):
            logger.warning(f"Normalized FQN in instanceof operator: \n {expr}")
            return InstanceOf(expr=expr.expr, type_name=expr.type_name.split(".")[-1])

        if isinstance(expr, Conditional):
            cond = self.normalize_expr(expr.cond)
            then = self.normalize_expr(expr.then)

            if expr.otherwise is None:
                # (c ? t)  ==>  (!c || t)
                norm_expr = Or(Not(cond), then)
                logger.critical(f"Normalized invalid Conditional Expression: \n {expr} -> {norm_expr}")
                return norm_expr

            otherwise = self.normalize_expr(expr.otherwise)
            return Conditional(cond, then, otherwise)

        if isinstance(expr, Compare) and expr.op == "==":
            left = self.normalize_expr(expr.left)
            right = self.normalize_expr(expr.right)

            # true == X   or   X == true
            if isinstance(left, BoolConst) and left.value is True and self._is_boolean_expr(right):
                return right
            if isinstance(right, BoolConst) and right.value is True and self._is_boolean_expr(left):
                return left

            # false == X   or   X == false
            if isinstance(left, BoolConst) and left.value is False and self._is_boolean_expr(right):
                logger.warning(f"Normalized boolean comparison: Not(expr={right})")
                return Not(right)
            if isinstance(right, BoolConst) and right.value is False and self._is_boolean_expr(left):
                logger.warning(f"Normalized boolean comparison: Not(expr={left})")
                return Not(left)

            return Compare(left, "==", right)

        if isinstance(expr, And):
            return And(left=self.normalize_expr(expr.left), right=self.normalize_expr(expr.right))
        if isinstance(expr, Or):
            return Or(self.normalize_expr(expr.left), self.normalize_expr(expr.right))

        if isinstance(expr, Not):
            return Not(self.normalize_expr(expr.expr))

        if isinstance(expr, Var) or isinstance(expr, BoolVar) or isinstance(expr, BoolConst) or isinstance(expr, IntConst):
            return expr



        return expr
