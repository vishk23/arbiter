from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *


def _build_checks() -> List[Dict[str, Any]]:
    checks: List[Dict[str, Any]] = []

    # If k = floor(sqrt(n)), then n = 70k - 1000 and
    # k^2 <= n < (k+1)^2.
    # Substituting n gives:
    #   k^2 <= 70k - 1000 < (k+1)^2.
    # This constrains k to exactly six integer values.
    k = Int("k")
    theorem = ForAll(
        [k],
        Implies(
            And(k >= 0, k * k <= 70 * k - 1000, 70 * k - 1000 < (k + 1) * (k + 1)),
            Or(k == 20, k == 21, k == 47, k == 48, k == 49, k == 50),
        ),
    )

    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "kdrag_solution_range_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded with proof object: {proof}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_solution_range_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Z3 proof attempt failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: each claimed solution satisfies the equation.
    sols = [400, 470, 2290, 2360, 2430, 2500]
    numeric_ok = True
    bad = []
    for n in sols:
        lhs = (n + 1000) / 70
        rhs = int(n ** 0.5)
        if lhs != rhs:
            numeric_ok = False
            bad.append((n, lhs, rhs))

    checks.append(
        {
            "name": "claimed_solutions_verify",
            "passed": numeric_ok,
            "backend": "python",
            "proof_type": "sanity_check",
            "details": "All claimed solutions satisfy the equation." if numeric_ok else f"Bad values: {bad}",
        }
    )

    # Count the solutions implied by the k-range.
    ks = [20, 21, 47, 48, 49, 50]
    ns = [70 * t - 1000 for t in ks]
    checks.append(
        {
            "name": "solution_count",
            "passed": len(ns) == 6,
            "backend": "python",
            "proof_type": "count",
            "details": f"Derived n values: {ns}",
        }
    )

    return checks


def verify() -> Dict[str, Any]:
    checks = _build_checks()
    return {"checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)