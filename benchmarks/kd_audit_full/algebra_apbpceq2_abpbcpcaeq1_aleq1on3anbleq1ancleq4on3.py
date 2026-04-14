from math import isfinite

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, sqrt, Rational, minimal_polynomial, simplify, N


def verify():
    checks = []
    proved = True

    # Check 1: rigorous algebraic identity from the hypotheses
    try:
        a, b, c = Reals("a b c")
        identity = kd.prove(
            ForAll(
                [a, b, c],
                Implies(
                    And(a + b + c == 2, a * b + b * c + c * a == 1),
                    a * a + b * b + c * c == 2,
                ),
            )
        )
        checks.append(
            {
                "name": "sum_squares_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(identity),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sum_squares_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove identity: {e}",
            }
        )

    # Check 2: symbolic zero certificate for the extremal case a=b=1/3, c=4/3
    try:
        x = Symbol("x")
        expr = (Rational(1, 3) + Rational(1, 3) + Rational(4, 3)) - 2
        mp = minimal_polynomial(expr, x)
        ok = mp == x
        checks.append(
            {
                "name": "extremal_case_sum_zero",
                "passed": bool(ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"minimal_polynomial(expr, x) = {mp}",
            }
        )
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "extremal_case_sum_zero",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Failed symbolic zero check: {e}",
            }
        )

    # Check 3: numerical sanity check at the equality case (0,1,1)
    try:
        va, vb, vc = 0.0, 1.0, 1.0
        cond1 = abs((va + vb + vc) - 2.0) < 1e-12
        cond2 = abs((va * vb + vb * vc + vc * va) - 1.0) < 1e-12
        bounds = (0.0 <= va <= 1.0 / 3.0) and (1.0 / 3.0 <= vb <= 1.0) and (1.0 <= vc <= 4.0 / 3.0)
        passed = cond1 and cond2 and bounds and all(isfinite(t) for t in [va, vb, vc])
        checks.append(
            {
                "name": "numerical_equality_case",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"(a,b,c)=({va},{vb},{vc}), sum={va+vb+vc}, pairwise={va*vb+vb*vc+vc*va}",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_equality_case",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Failed numerical sanity check: {e}",
            }
        )

    # Check 4: note on full theorem verification status
    # The full monotonic/inequality argument from the prompt is not directly encoded here as a single
    # kdrag certificate, so we conservatively report the overall theorem as not fully proved.
    if proved:
        # We intentionally require a certified proof of the full bound package; not available here.
        proved = False
        checks.append(
            {
                "name": "full_bounds_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "Full bound theorem not encoded as a single verified certificate in this module.",
            }
        )
    else:
        checks.append(
            {
                "name": "full_bounds_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "Overall theorem not fully proved; only partial verified checks were established.",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)