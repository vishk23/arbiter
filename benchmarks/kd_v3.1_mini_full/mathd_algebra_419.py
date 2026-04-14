from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Certified proof: directly prove that substituting a = -1 and b = 5
    # into -a - b^2 + 3ab yields -39.
    try:
        a, b = Ints("a b")
        expr = -a - b * b + 3 * a * b
        goal = substitute(expr, (a, IntVal(-1)), (b, IntVal(5))) == IntVal(-39)
        prf = kd.prove(goal)
        checks.append(
            {
                "name": "substitution_evaluates_to_negative_39",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kdrag proof object: {prf}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "substitution_evaluates_to_negative_39",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove substituted value: {type(e).__name__}: {e}",
            }
        )

    # Additional certified proof: arithmetic simplification with concrete integers.
    try:
        value_goal = IntVal(-(-1) - (5 ** 2) + 3 * (-1) * 5) == IntVal(-39)
        prf2 = kd.prove(value_goal)
        checks.append(
            {
                "name": "direct_arithmetic_computation",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified direct arithmetic evaluation: {prf2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "direct_arithmetic_computation",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed direct arithmetic proof: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check, kept only as an additional check.
    numeric_value = -(-1) - (5 ** 2) + 3 * (-1) * 5
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": numeric_value == -39,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed value is {numeric_value}; expected -39.",
        }
    )

    if not all(ch["passed"] for ch in checks):
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)