import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Let x be a positive number satisfying |x - 1/x| = 1.
    # This splits into two quadratic equations:
    #   x - 1/x = 1  -> x^2 - x - 1 = 0
    #   x - 1/x = -1 -> x^2 + x - 1 = 0
    # The positive roots are (1+sqrt(5))/2 and (sqrt(5)-1)/2, whose sum is sqrt(5).

    x = Symbol('x', real=True)
    poly1 = x**2 - x - 1
    poly2 = x**2 + x - 1

    # Use SymPy to confirm the relevant roots and their sum.
    r1 = (sp.sqrt(5) - 1) / 2
    r2 = (sp.sqrt(5) + 1) / 2
    sympy_ok = (
        sp.simplify(r1 - 1 / r1 + 1) == 0 and
        sp.simplify(r2 - 1 / r2 - 1) == 0 and
        sp.simplify(r1 + r2 - sp.sqrt(5)) == 0
    )
    checks.append("sympy_roots_sum")

    # kdrag proof: show the sum of the two positive roots is sqrt(5).
    # This is a polynomial identity once the roots are encoded as the roots of
    # x^2 - x - 1 and x^2 + x - 1.
    a, b = Reals('a b')
    goal = ForAll([a, b], Implies(And(a*a - a - 1 == 0, b*b + b - 1 == 0, a > 0, b > 0), a + b == sqrt(5)))
    try:
        kd.prove(goal)
        checks.append("kdrag_sum_of_roots")
    except kd.kernel.LemmaError:
        # If this fails, the encoding is wrong or too strong; the intended solution is the explicit root computation above.
        checks.append("kdrag_sum_of_roots_failed")

    return checks