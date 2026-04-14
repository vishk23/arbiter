from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Int, And, ForAll, Implies


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Verified proof: the divisibility criterion for 11 implies the blank digit is 5.
    # For the number 20_7, the alternating sum of digits is 2 - 0 + A - 7 = A - 5.
    # A multiple of 11 in the range [-9, 9] can only be 0, so A = 5.
    try:
        A = Int("A")
        thm = kd.prove(
            ForAll([A], Implies(And(A >= 0, A <= 9, (A - 5) % 11 == 0), A == 5))
        )
        checks.append(
            {
                "name": "digit_is_5_verified_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded with certificate: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "digit_is_5_verified_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: substitute A = 5 and verify the alternating sum is 0.
    try:
        A_val = 5
        alternating_sum = 2 - 0 + A_val - 7
        passed = alternating_sum == 0
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For A=5, alternating sum = {alternating_sum}; divisible by 11 criterion satisfied.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
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