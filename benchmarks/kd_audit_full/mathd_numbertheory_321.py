from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Int, IntVal, ForAll, Implies


# The theorem: 1058 is the multiplicative inverse of 160 modulo 1399.
# We verify it with a formal Z3-backed proof and add a numerical sanity check.


def _prove_inverse() -> object:
    n = IntVal(1058)
    mod = IntVal(1399)
    lhs = n * IntVal(160)
    # Prove the exact modular equality for the concrete instance.
    return kd.prove(lhs % mod == IntVal(1))


# Precompute the proof object at import time so it is tamper-proof.
PROOF_1058 = _prove_inverse()


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Verified proof check (certificate from kdrag/Z3).
    try:
        proof = PROOF_1058
        checks.append(
            {
                "name": "1058_is_inverse_mod_1399",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove() succeeded: {proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "1058_is_inverse_mod_1399",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Formal proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check.
    try:
        val = (1058 * 160) % 1399
        passed = (val == 1)
        proved = proved and passed
        checks.append(
            {
                "name": "numerical_sanity_1058_times_160_mod_1399",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"(1058 * 160) % 1399 = {val}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_1058_times_160_mod_1399",
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