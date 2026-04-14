from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Verified proof: from 2^a = 32 = 2^5, infer a = 5.
    # Then from a^b = 125 and a = 5, infer b = 3.
    # Finally compute b^a = 3^5 = 243.
    a = Int("a")
    b = Int("b")

    try:
        thm_a = kd.prove(ForAll([a], Implies(2 ** a == 32, a == 5)))
        checks.append(
            {
                "name": "derive_a_equals_5_from_2_pow_a_equals_32",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm_a),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "derive_a_equals_5_from_2_pow_a_equals_32",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    try:
        thm_b = kd.prove(ForAll([b], Implies(5 ** b == 125, b == 3)))
        checks.append(
            {
                "name": "derive_b_equals_3_from_5_pow_b_equals_125",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm_b),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "derive_b_equals_3_from_5_pow_b_equals_125",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # Direct verified certificate for the final value.
    try:
        thm_final = kd.prove(3 ** 5 == 243)
        checks.append(
            {
                "name": "compute_b_pow_a_equals_243",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm_final),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "compute_b_pow_a_equals_243",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # Numerical sanity check at the concrete values a=5, b=3.
    num_ok = (2 ** 5 == 32) and (5 ** 3 == 125) and (3 ** 5 == 243)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Checked 2^5 = 32, 5^3 = 125, and 3^5 = 243.",
        }
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)