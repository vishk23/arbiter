from __future__ import annotations

from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import Int, Exists, ForAll, Implies, And, Not


def _kdrag_proof_remainder_194_mod_11():
    n = Int("n")
    r = Int("r")
    # Prove existence of quotient/remainder decomposition for the concrete number 194.
    # This is a certificate that 194 = 17*11 + 7, hence 194 mod 11 = 7.
    theorem = Exists([n, r], And(194 == n * 11 + r, r == 7))
    return kd.prove(theorem)


def _numerical_sanity_check() -> Dict[str, Any]:
    value = 194 % 11
    passed = (value == 7)
    return {
        "name": "194 mod 11 == 7",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed 194 % 11 = {value}."
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof certificate via kdrag/Z3.
    try:
        proof = _kdrag_proof_remainder_194_mod_11()
        checks.append({
            "name": "Existential decomposition 194 = 11*n + 7",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned certificate: {proof}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "Existential decomposition 194 = 11*n + 7",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}"
        })

    # Direct arithmetic check, also conceptually verified by the hint.
    try:
        q = 17
        r = 7
        passed = (194 == q * 11 + r) and (r == 7)
        checks.append({
            "name": "Concrete witness 17 and 7",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked 194 = {q}*11 + {r}."
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "Concrete witness 17 and 7",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    num_check = _numerical_sanity_check()
    checks.append(num_check)
    if not num_check["passed"]:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)