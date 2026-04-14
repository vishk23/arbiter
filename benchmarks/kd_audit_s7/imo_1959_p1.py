from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, Ints, ForAll, Implies, And


def _check_irreducible_gcd_proof() -> Dict[str, Any]:
    """Verified proof that gcd(21n+4, 14n+3) = 1 for all natural n."""
    n, d = Ints("n d")
    try:
        # If d divides both 21n+4 and 14n+3, then d must be 1.
        # This is equivalent to the Euclidean algorithm argument in the statement.
        thm = kd.prove(
            ForAll(
                [n, d],
                Implies(
                    And(n >= 0, d > 0, (21 * n + 4) % d == 0, (14 * n + 3) % d == 0),
                    d == 1,
                ),
            )
        )
        passed = True
        details = f"Verified by kdrag certificate: {thm}"
    except Exception as e:
        passed = False
        details = f"kdrag proof failed: {type(e).__name__}: {e}"
    return {
        "name": "gcd_divides_implies_one",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    }


def _check_euclidean_step() -> Dict[str, Any]:
    """A direct symbolic check of the Euclidean-algorithm reduction."""
    n = Int("n")
    try:
        thm = kd.prove(ForAll([n], (21 * n + 4) - (14 * n + 3) == 7 * n + 1))
        passed = True
        details = f"Verified algebraic reduction certificate: {thm}"
    except Exception as e:
        passed = False
        details = f"Symbolic reduction proof failed: {type(e).__name__}: {e}"
    return {
        "name": "euclidean_reduction_step",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    }


def _check_numerical_sanity() -> Dict[str, Any]:
    """Concrete numerical sanity check for a sample n."""
    n = 5
    num = 21 * n + 4
    den = 14 * n + 3
    import math

    g = math.gcd(num, den)
    passed = (num == 109) and (den == 73) and (g == 1)
    details = f"For n={n}, numerator={num}, denominator={den}, gcd={g}."
    return {
        "name": "sample_numerical_gcd",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_check_euclidean_step())
    checks.append(_check_irreducible_gcd_proof())
    checks.append(_check_numerical_sanity())
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)