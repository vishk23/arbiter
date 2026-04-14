from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, expand, diff


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: Verified proof by completing the square.
    x = Real("x")
    expr = x * x - 14 * x + 3
    sq_form = (x - 7) * (x - 7) - 46
    try:
        proof_eq = kd.prove(ForAll([x], expr == sq_form))
        proof_min = kd.prove(ForAll([x], expr >= -46), by=[proof_eq])
        proof_at_7 = kd.prove((RealVal(7) * RealVal(7)) - 14 * RealVal(7) + 3 == -46)
        checks.append({
            "name": "completing_square_minimum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified that x^2 - 14x + 3 = (x - 7)^2 - 46 and therefore is bounded below by -46; minimum occurs at x = 7. Proofs: {proof_eq}, {proof_min}, {proof_at_7}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "completing_square_minimum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify the square-completion argument: {type(e).__name__}: {e}",
        })

    # Check 2: Numerical sanity check at concrete values.
    try:
        vals = {6: 6 * 6 - 14 * 6 + 3, 7: 7 * 7 - 14 * 7 + 3, 8: 8 * 8 - 14 * 8 + 3}
        passed = vals[7] < vals[6] and vals[7] < vals[8] and vals[7] == -46
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"f(6)={vals[6]}, f(7)={vals[7]}, f(8)={vals[8]}; confirms the minimum value is attained at x=7.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
        })

    # Check 3: Symbolic differentiation confirms the critical point x = 7.
    try:
        xs = Symbol("xs", real=True)
        f = xs**2 - 14 * xs + 3
        df = diff(f, xs)
        critical = expand(df)
        passed = str(critical) == "2*xs - 14"
        if not passed:
            proved = False
        checks.append({
            "name": "symbolic_critical_point",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Derivative is {critical}; setting it to zero gives xs = 7.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "symbolic_critical_point",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Symbolic derivative check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)