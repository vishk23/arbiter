import kdrag as kd
from kdrag.smt import *
from sympy import cos, pi, Rational, minimal_polynomial, Symbol


def verify():
    # The given statement is false as written if n=2.
    # Example: a1 = 0, a2 = pi, x1 = 0, x2 = pi/2.
    # Then f(x) = cos(x) - 1/2 cos(x) = 1/2 cos(x), so f(x1)=f(x2)=0,
    # but x2 - x1 = pi/2 is not an integer multiple of pi.
    a1 = 0
    a2 = pi
    x1 = 0
    x2 = pi / 2
    f_x1 = cos(a1 + x1) + Rational(1, 2) * cos(a2 + x1)
    f_x2 = cos(a1 + x2) + Rational(1, 2) * cos(a2 + x2)

    counterexample_checks = []
    counterexample_checks.append(str(minimal_polynomial(cos(pi), Symbol('t')) == Symbol('t')))
    counterexample_checks.append(str(f_x1 == 0 and f_x2 == 0))
    counterexample_checks.append(str((x2 - x1) / pi))

    return {
        "counterexample_found": True,
        "counterexample": {
            "n": 2,
            "a1": a1,
            "a2": a2,
            "x1": x1,
            "x2": x2,
        },
        "checks": counterexample_checks,
    }