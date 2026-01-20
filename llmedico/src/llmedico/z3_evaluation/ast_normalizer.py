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

    def normalize_expr(self, expr: Expr) -> Optional[Expr]:

        # ---- Method calls ----
        if isinstance(expr, Method):

            if expr.name == "Arrays" and isinstance(expr.receiver, Method) and expr.parameters == []: # java.utils.Array = Method=(receiver=(Method(receiver=Var(name='java'), name='util', parameters=[]), name='Arrays', parameters=[])
                return self.normalize_expr(expr.receiver)


            if expr.name == "util" and isinstance(expr.receiver, Var) and expr.receiver.name == "java": # java.utils = Method(receiver=Var(name='java'), name='util', parameters=[])
                return None

            if expr.name == "stream": # java.utils.Arrays.stream(args[0]) -> args[0].stream()

                receiver = self.normalize_expr(expr.receiver) if expr.receiver else None #reciever can be Method or Var (OBJ)
                parameters = expr.parameters

                if not receiver and parameters and len(parameters) == 1: #stream(args[0]) -> args[0].stream()
                    normalized_method = Method(receiver=parameters[0], name=expr.name, parameters=[])
                    logger.warning(f"Normalized java.utils.Arrays.stream()\nbefore: {expr}\nafter: {normalized_method}")
                    return normalized_method
                elif receiver and parameters and len(parameters) == 1: # java.util.Arrays.stream(args[0])

                    return Method(receiver=receiver, name=expr.name, parameters=expr.parameters)

            elif isinstance(expr.receiver, Method): #java.utils.Arrays.stream(args[0]).anyMatch(e -> e==null)
                normalized_receiver = self.normalize_expr(expr.receiver)
                return Method(receiver=normalized_receiver, name=expr.name, parameters=expr.parameters)

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
