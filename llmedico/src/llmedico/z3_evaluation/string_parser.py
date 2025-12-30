from llmedico.z3_evaluation.model_ast import *


class ParseError(Exception):
    pass


class StringParser:
    """
    We implement operator precedence:
    1.||
    2.&&
    3.comparisons
    4.Addition / Subtraction
    5.Multiplication
    6.unary ! -
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

    # OR
    def parse_expr(self) -> Expr:
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

    # Multiplication
    def _parse_mul(self) -> Expr:
        expr = self._parse_unary()
        while self.peek() == "*":
            self.consume("*")
            expr = Mul(expr, self._parse_unary())
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

        if tok.isdigit():
            self.consume()
            return IntConst(int(tok))

        if tok.isidentifier():
            self.consume()
            # default assumption: boolean variable TODO
            return Var(tok)

        if tok == "(":
            self.consume("(")
            expr = self.parse_expr()
            self.consume(")")
            return expr

        raise ParseError(f"Unexpected token: {tok}")

    def parse(self) -> Expr:
        ast = self.parse_expr()
        if self.peek() is not None:
            raise ParseError("Extra tokens at end")
        return ast