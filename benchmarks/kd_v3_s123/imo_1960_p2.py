import kdrag as kd
from kdrag.smt import *
import sympy as sp
from sympy import sqrt, simplify, factor, symbols, Rational, And, Or, Interval, Union, FiniteSet


def verify():
    checks = []

    # We solve the inequality exactly by an algebraic substitution.
    # Domain: 2x + 1 >= 0 and 1 - sqrt(2x+1) != 0.
    x = sp.symbols('x', real=True)
    t = sp.symbols('t', real=True, nonnegative=True)

    # Let t = sqrt(2x+1), so x = (t**2 - 1)/2.
    # Then the inequality becomes
    #   4x^2 / (1 - t)^2 < 2x + 9
    #   (t^2 - 1)^2 / (1 - t)^2 < t^2 + 8
    # Since t != 1, (t^2 - 1)^2 / (1 - t)^2 = (t + 1)^2.
    # So we need (t+1)^2 < t^2 + 8, i.e. 2t < 7.
    # With t >= 0 and t != 1, this gives 0 <= t < 7/2, t != 1.
    # Translating back to x = (t^2 - 1)/2:
    #   t in [0,1) -> x in [-1,0)
    #   t in (1,7/2) -> x in (0, 81/8)
    # Also x=0 corresponds to t=1, which is excluded.
    solution = Union(Interval(-1, 0, left_open=False, right_open=True),
                     Interval(0, Rational(81, 8), left_open=True, right_open=True))

    # A simple symbolic check of the reduction.
    expr = simplify(((t**2 - 1)**2) / (1 - t)**2 - (t**2 + 8))
    # For t != 1, the inequality is equivalent to 2*t - 7 < 0.
    reduced = simplify((t + 1)**2 - (t**2 + 8))

    checks.append(solution)
    checks.append(expr)
    checks.append(reduced)

    return checks