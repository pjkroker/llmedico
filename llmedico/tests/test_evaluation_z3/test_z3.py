from z3 import *

def test_1():
    x = Real('x')
    y = Real('y')
    s = Solver()
    s.add(x + y > 5, x > 1, y > 1)
    print(s.check())
    print(s.model())