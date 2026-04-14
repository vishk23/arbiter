from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # For any natural number n, 11 divides 10^n - (-1)^n.
    # Use Z3's Mod on integers explicitly; exponentiation by a symbolic Int is not
    # directly supported in a way that makes % applicable here, so we prove the
    # equivalent divisibility statement by checking the expression modulo 11.
    n = Int("n")
    term = If(n % 2 == 0, 10 ** n - 1, 10 ** n + 1)
    theorem = ForAll([n], Implies(n >= 0, Mod(term, 11) == 0))

    try:
        proof = kd.prove(theorem)
        checks.append({
            "name": "divisibility_theorem",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by kd.prove(); certificate: {proof}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "divisibility_theorem",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at a concrete value.
    n0 = 7
    lhs = 10 ** n0 - (-1) ** n0
    numerical_passed = (lhs % 11 == 0)
    checks.append({
        "name": "numerical_sanity_n7",
        "passed": numerical_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At n={n0}, 10^n - (-1)^n = {lhs}, remainder mod 11 is {lhs % 11}.",
    })
    if not numerical_passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)