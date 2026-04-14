from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies


def _proved_check(name: str, passed: bool, backend: str, proof_type: str, details: str) -> Dict[str, object]:
    return {
        "name": name,
        "passed": passed,
        "backend": backend,
        "proof_type": proof_type,
        "details": details,
    }


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []

    # Verified proof: if (x-9)/(x+1) = 2 and x != -1, then x = -11.
    # Encode without division by cross-multiplication.
    x = Int("x")
    theorem = ForAll(
        [x],
        Implies(
            x != -1,
            Implies(x - 9 == 2 * (x + 1), x == -11),
        ),
    )
    try:
        proof = kd.prove(theorem)
        checks.append(
            _proved_check(
                name="cross_multiplication_implies_x_eq_minus_11",
                passed=True,
                backend="kdrag",
                proof_type="certificate",
                details=f"kd.prove succeeded: {proof}",
            )
        )
    except Exception as e:
        checks.append(
            _proved_check(
                name="cross_multiplication_implies_x_eq_minus_11",
                passed=False,
                backend="kdrag",
                proof_type="certificate",
                details=f"Proof failed: {type(e).__name__}: {e}",
            )
        )

    # Numerical sanity check at the claimed solution x = -11.
    try:
        xv = -11
        lhs = (xv - 9) / (xv + 1)
        passed = abs(lhs - 2) == 0
        checks.append(
            _proved_check(
                name="numeric_substitution_at_minus_11",
                passed=passed,
                backend="numerical",
                proof_type="numerical",
                details=f"Substituting x=-11 gives lhs={lhs}, expected 2.",
            )
        )
    except Exception as e:
        checks.append(
            _proved_check(
                name="numeric_substitution_at_minus_11",
                passed=False,
                backend="numerical",
                proof_type="numerical",
                details=f"Numerical check failed: {type(e).__name__}: {e}",
            )
        )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)