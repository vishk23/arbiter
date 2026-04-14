from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Ints, ForAll, Implies


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: factorization implies coefficient equations and the target value AB + B = 12.
    # Let (Ax - 8)(Bx + 3) = AB x^2 + (3A - 8B)x - 24.
    # Matching with 10x^2 - x - 24 gives AB = 10 and 3A - 8B = -1.
    # The unique integer solution is A = 5, B = 2, hence AB + B = 12.
    A, B = Ints("A B")
    x = kd.smt.Int("x")

    try:
        # Main verified claim: under the factorization coefficients, AB+B=12.
        thm = kd.prove(
            ForAll(
                [A, B],
                Implies(
                    (A * B == 10) & (3 * A - 8 * B == -1),
                    A * B + B == 12,
                ),
            )
        )
        checks.append(
            {
                "name": "coefficients_imply_AB_plus_B_equals_12",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "coefficients_imply_AB_plus_B_equals_12",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # A second verified proof: the factorization itself is algebraically consistent.
    # (5x-8)(2x+3) == 10x^2 - x - 24 for all x.
    try:
        thm2 = kd.prove(
            ForAll(
                [x],
                (5 * x - 8) * (2 * x + 3) == 10 * x * x - x - 24,
            )
        )
        checks.append(
            {
                "name": "factorization_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm2),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "factorization_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # Numerical sanity check at a concrete value.
    xv = 2
    lhs = 10 * xv * xv - xv - 24
    rhs = (5 * xv - 8) * (2 * xv + 3)
    checks.append(
        {
            "name": "numerical_sanity_at_x_equals_2",
            "passed": lhs == rhs == 14,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"lhs={lhs}, rhs={rhs}, AB+B=12",
        }
    )
    if not (lhs == rhs == 14):
        proved = False

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)