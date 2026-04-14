from __future__ import annotations

from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: verified symbolic proof of subadditivity on nonnegative reals:
    # For x,y >= 0, x/(1+x) + y/(1+y) - (x+y)/(1+x+y) = xy(2+x+y)/((1+x)(1+y)(1+x+y)) >= 0.
    x, y = Reals("x y")
    lhs = x / (1 + x) + y / (1 + y) - (x + y) / (1 + x + y)
    thm1 = ForAll([x, y], Implies(And(x >= 0, y >= 0), lhs >= 0))
    try:
        pf1 = kd.prove(thm1)
        checks.append(
            {
                "name": "subadditivity_of_t_over_1_plus_t",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified by kdrag proof object: {pf1}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "subadditivity_of_t_over_1_plus_t",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: verified inequality using triangle inequality and monotonicity of t/(1+t).
    a, b = Reals("a b")
    aa, bb = Abs(a), Abs(b)
    ab = Abs(a + b)
    goal = ab / (1 + ab) <= aa / (1 + aa) + bb / (1 + bb)
    thm2 = ForAll([a, b], goal)
    try:
        pf2 = kd.prove(thm2)
        checks.append(
            {
                "name": "main_abs_inequality",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified by kdrag proof object: {pf2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "main_abs_inequality",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at concrete values.
    aval = 2.0
    bval = -3.5
    lhs_num = abs(aval + bval) / (1.0 + abs(aval + bval))
    rhs_num = abs(aval) / (1.0 + abs(aval)) + abs(bval) / (1.0 + abs(bval))
    num_pass = lhs_num <= rhs_num + 1e-12
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(num_pass),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At a={aval}, b={bval}: lhs={lhs_num}, rhs={rhs_num}.",
        }
    )
    if not num_pass:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)