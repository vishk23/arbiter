from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Int, And, Implies, ForAll


# We prove the theorem using modular arithmetic in Z3 via Knuckledragger.
# Statement: if 0 <= n < 101 and 123456 ≡ n mod 101, then n = 34.


def _prove_mod_equiv_34():
    n = Int("n")
    thm = kd.prove(
        ForAll(
            [n],
            Implies(
                And(n >= 0, n < 101, (123456 - n) % 101 == 0),
                n == 34,
            ),
        )
    )
    return thm


MOD_PROOF = None


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Verified proof check using kdrag.
    try:
        proof = _prove_mod_equiv_34()
        checks.append(
            {
                "name": "modular_congruence_uniqueness",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "modular_congruence_uniqueness",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check.
    lhs = 123456 % 101
    rhs = 34 % 101
    num_passed = lhs == rhs and 0 <= 34 < 101
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": num_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"123456 % 101 = {lhs}, 34 % 101 = {rhs}, range check 0<=34<101 is {0 <= 34 < 101}",
        }
    )
    if not num_passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)