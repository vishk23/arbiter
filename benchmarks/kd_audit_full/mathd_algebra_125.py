from __future__ import annotations

from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import Int, And, ForAll, Implies


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Verified proof: encode the algebraic conditions and prove the son's age is 6.
    x = Int("x")
    y = Int("y")
    try:
        proof = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(y == 5 * x, (x - 3) + (y - 3) == 30),
                    x == 6,
                ),
            )
        )
        checks.append(
            {
                "name": "algebraic_solution_is_6",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved with kd.prove(): {proof}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "algebraic_solution_is_6",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete solution x=6, y=30.
    x0 = 6
    y0 = 30
    passed_num = (y0 == 5 * x0) and ((x0 - 3) + (y0 - 3) == 30)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(passed_num),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked x={x0}, y={y0}: father=5*son and three-years-ago sum=30.",
        }
    )

    proved = all(c["passed"] for c in checks) and any(
        c["passed"] and c["proof_type"] == "certificate" for c in checks
    )
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)