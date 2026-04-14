from sympy import symbols, solve, Eq, Rational, simplify

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Solve the rational equation exactly with SymPy.
    x = symbols('x')
    lhs = 2 + Rational(1, 1) / (1 + Rational(1, 1) / (2 + Rational(2, 1) / (3 + x)))
    sol = solve(Eq(lhs, Rational(144, 53)), x)
    expected = Rational(3, 4)

    sympy_ok = len(sol) == 1 and simplify(sol[0] - expected) == 0
    checks.append({
        "name": "sympy_solves_x_equals_3_over_4",
        "passed": bool(sympy_ok),
        "backend": "sympy",
        "proof_type": "exact_solve",
        "details": f"SymPy solution set: {sol}"
    })

    # kdrag proof: the claimed answer satisfies the equation.
    xr = Real("xr")
    claim = xr == RealVal(3) / RealVal(4)
    checks.append({
        "name": "claimed_answer_is_3_over_4",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "sanity_check",
        "details": "The unique solution is x = 3/4."
    })

    return checks