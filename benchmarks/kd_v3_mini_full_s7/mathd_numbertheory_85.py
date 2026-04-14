from __future__ import annotations

from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies


# Formal statement: the base-3 numeral 1222_3 evaluates to 53 in base 10.
# We prove the concrete arithmetic identity with kdrag/Z3.

def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: direct arithmetic certificate via kdrag.
    try:
        thm = kd.prove((1 * 3**3) + (2 * 3**2) + (2 * 3) + 2 == 53)
        checks.append(
            {
                "name": "base3_to_base10_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned certificate: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "base3_to_base10_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof attempt failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete value.
    try:
        value = (1 * 3**3) + (2 * 3**2) + (2 * 3) + 2
        ok = (value == 53)
        checks.append(
            {
                "name": "numerical_evaluation",
                "passed": bool(ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed value {(value)}; expected 53.",
            }
        )
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_evaluation",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    # Optional symbolic check using plain exact arithmetic; this is not the primary certificate.
    try:
        from sympy import Integer

        expr = Integer(1) * 3**3 + Integer(2) * 3**2 + Integer(2) * 3 + Integer(2)
        ok = int(expr) == 53
        checks.append(
            {
                "name": "sympy_exact_arithmetic",
                "passed": bool(ok),
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"SymPy exact evaluation gives {expr}.",
            }
        )
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_exact_arithmetic",
                "passed": False,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"SymPy check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)