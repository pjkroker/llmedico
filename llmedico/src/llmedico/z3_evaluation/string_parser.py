from llmedico.z3_evaluation.model_ast import *
import logging
logger = logging.getLogger(__name__)

class ParseError(Exception):
    pass


class StringParser:
    """
    We implement operator precedence:
    1.?
    2.||
    3.&&
    4.comparisons
    5.Addition / Subtraction
    6.Multiplication
    7.unary ! -
    7.atoms
    """
    def __init__(self, tokens: list[str]):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def consume(self, expected=None):
        tok = self.peek()
        if tok is None:
            raise ParseError("Unexpected end")
        if expected and tok != expected:
            raise ParseError(f"Expected {expected}, got {tok}")
        self.pos += 1
        return tok

    #?
    def parse_expr(self) -> Expr:
        expr = self._parse_or()
        if self.peek() == "?":
            self.consume("?")
            then = self.parse_expr()
            self.consume(":")
            otherwise = self.parse_expr()
            return Conditional(expr, then, otherwise)
        return expr

    # OR
    def _parse_or(self) -> Expr:
        expr = self._parse_and()
        while self.peek() == "||":
            self.consume("||")
            expr = Or(expr, self._parse_and())
        return expr

    # AND
    def _parse_and(self) -> Expr:
        expr = self._parse_cmp()
        while self.peek() == "&&":
            self.consume("&&")
            expr = And(expr, self._parse_cmp())
        return expr

    # Comparison
    def _parse_cmp(self) -> Expr:
        left = self._parse_add()
        if self.peek() in {">", ">=", "<", "<=", "==", "!="}:
            op = self.consume()
            right = self._parse_add()
            return Compare(left, op, right)
        return left

    # Addition and Subtraction
    def _parse_add(self) -> Expr:
        expr = self._parse_mul()
        while self.peek() in {"+", "-"}:
            op = self.consume()
            right = self._parse_mul()
            if op == "+":
                expr = Add(expr, right)
            else:
                expr = Sub(expr, right)
        return expr

    # Multiplication, Division, Modulo
    def _parse_mul(self) -> Expr:
        expr = self._parse_unary()
        while self.peek() in {"*", "/", "%"}:
            op = self.consume()
            right = self._parse_unary()
            if op == "*":
                expr = Mul(expr, right)
            elif op == "/":
                expr = Div(expr, right)
            else:  # %
                expr = Mod(expr, right)
        return expr

    # Unary
    def _parse_unary(self) -> Expr:
        if self.peek() == "!":
            self.consume("!")
            return Not(self._parse_unary())

        if self.peek() == "-":
            self.consume("-")
            return UnaryMinus(self._parse_unary())

        return self._parse_atom()

    # Atom
    def _parse_atom(self) -> Expr:
        tok = self.peek()

        if tok is None:
            raise ParseError("Unexpected end")

        # Ignore casts: (Type) expr
        if self._try_parse_cast():
            return self._parse_atom()

        if tok.isdigit():
            self.consume()
            return IntConst(int(tok))

        if tok.isidentifier():# default assumption: boolean variable TODO?
            self.consume()
            if tok == "true":
                return BoolConst(True)
            if tok == "false":
                return BoolConst(False)
            if tok == "null":
                return NullConst()

            # function / method call
            if self.peek() == "(":
                self.consume("(")
                args = self._parse_args()
                self.consume(")")
                return Method(receiver=None, name=tok, parameters=args)
            else:
                expr = Var(tok)
            return self._parse_postfix(expr)

        if tok == "(":
            self.consume("(")
            expr = self.parse_expr()
            self.consume(")")
            return expr

        raise ParseError(f"Unexpected token: {tok}")

    def _parse_args(self) -> list[Expr]:
        args = []

        if self.peek() == ")":
            return args

        while True:
            args.append(self.parse_expr())
            if self.peek() == ",":
                self.consume(",")
            else:
                break

        return args

    def _parse_postfix(self, expr: Expr) -> Expr:
        while self.peek() == ".":
            self.consume(".")
            name = self.consume()  # method name
            if not name.isidentifier():
                raise ParseError("Expected method name after '.'")

            self.consume("(")
            args = self._parse_args()
            self.consume(")")

            expr = Method(receiver=expr, name=name, parameters=args)

        return expr

    def _try_parse_cast(self):
        # Lookahead for: '(' Identifier ('.' Identifier)* ')'
        if self.peek() != "(":
            return False

        save = self.pos
        self.consume("(")

        if not self.peek() or not self.peek().isidentifier():
            self.pos = save
            return False

        self.consume()  # first identifier

        while self.peek() == ".":
            self.consume(".")
            if not self.peek() or not self.peek().isidentifier():
                self.pos = save
                return False
            self.consume()

        if self.peek() != ")":
            self.pos = save
            return False

        self.consume(")")
        logger.warning(f"Ignoring Casting expression")
        return True

    def parse(self) -> Expr:
        ast = self.parse_expr()
        if self.peek() is not None:
            raise ParseError(f"Extra tokens at end: {self.peek()}")
        return ast