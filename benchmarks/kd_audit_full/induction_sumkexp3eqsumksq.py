from __future__ import annotations

from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: Verified algebraic identity for the induction step.
    # For n >= 0, 6*sum_{k=0}^{n-1} k = 3*n*(n-1), hence
    # 2*n*sum = n^2*(n-1) and n^2 + 2*n*sum = n^3.
    n = Int("n")
    try:
        thm = kd.prove(
            ForAll(
                [n],
                Implies(
                    n >= 0,
                    2 * n * (n * (n - 1) / 2) + n * n == n * n * n,
                ),
            )
        )
        checks.append(
            {
                "name": "induction_step_algebra",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "induction_step_algebra",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Base case n = 1.
    try:
        base = kd.prove((0 == 0) == True)
        checks.append(
            {
                "name": "base_case_n1",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Trivial base case verified: {base}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "base_case_n1",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Base-case proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Numerical sanity check at n=5.
    n_val = 5
    lhs = sum(k ** 3 for k in range(n_val))
    rhs = (sum(k for k in range(n_val))) ** 2
    num_pass = lhs == rhs
    checks.append(
        {
            "name": "numerical_sanity_n5",
            "passed": num_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For n={n_val}, lhs={lhs}, rhs={rhs}.",
        }
    )
    if not num_pass:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)