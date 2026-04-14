from __future__ import annotations

from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import *

from sympy import Rational, Symbol, simplify


# The theorem states that if 5 plus 500% of 10 equals 110% of x,
# then x = 50.
# We verify this exactly with kdrag over the reals.

def _prove_main_theorem():
    x = Real("x")
    premise = 5 + Rational(500, 100) * 10 == Rational(110, 100) * x
    goal = x == 50
    thm = kd.prove(ForAll([x], Implies(premise, goal)))
    return thm


# A symbolic arithmetic sanity check.
def _symbolic_sanity():
    x = Symbol("x")
    expr_left = 5 + Rational(500, 100) * 10
    expr_right = Rational(110, 100) * x
    # Substitute x = 50 and confirm both sides match.
    lhs_val = simplify(expr_left)
    rhs_val = simplify(expr_right.subs(x, 50))
    return lhs_val == rhs_val == 55


# A numerical sanity check on the concrete value x = 50.
def _numerical_sanity():
    left = 5 + (500 / 100) * 10
    right = (110 / 100) * 50
    return abs(left - right) < 1e-12 and abs(left - 55) < 1e-12


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof certificate via kdrag.
    try:
        pf = _prove_main_theorem()
        checks.append(
            {
                "name": "main_theorem",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove() succeeded: {pf}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "main_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove() failed: {type(e).__name__}: {e}",
            }
        )

    # Symbolic sanity check.
    try:
        ok = _symbolic_sanity()
        checks.append(
            {
                "name": "symbolic_sanity",
                "passed": bool(ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": "Substituting x=50 gives equality 55 = 55.",
            }
        )
        proved = proved and bool(ok)
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "symbolic_sanity",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Symbolic check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check.
    try:
        ok = _numerical_sanity()
        checks.append(
            {
                "name": "numerical_sanity",
                "passed": bool(ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Direct floating-point evaluation at x=50 yields matching values.",
            }
        )
        proved = proved and bool(ok)
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)