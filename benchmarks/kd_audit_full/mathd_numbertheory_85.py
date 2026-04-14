from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, IntVal


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Verified proof: the base-3 expansion 1222_3 equals 53 in base 10.
    # We prove the arithmetic equality in Z3 via kdrag.
    val = Int("val")
    try:
        proof = kd.prove(val == IntVal(53), by=[val == IntVal(2) + IntVal(2) * IntVal(3) + IntVal(2) * IntVal(9) + IntVal(27)])
        checks.append(
            {
                "name": "base3_to_base10_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {proof}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "base3_to_base10_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete value 1222_3.
    digits_value = 1 * (3 ** 3) + 2 * (3 ** 2) + 2 * (3 ** 1) + 2 * (3 ** 0)
    numeric_passed = digits_value == 53
    checks.append(
        {
            "name": "numerical_evaluation",
            "passed": bool(numeric_passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed 1*3^3 + 2*3^2 + 2*3 + 2 = {digits_value}.",
        }
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)