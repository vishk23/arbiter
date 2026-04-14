from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify() -> dict:
    checks: List[dict] = []
    proved = True

    # Verified proof: if sqrt(19 + 3y) = 7, then y = 10.
    # We encode the core algebraic implication as a universally quantified theorem.
    y = Real("y")
    thm = None
    try:
        thm = kd.prove(
            ForAll(
                [y],
                Implies(
                    And(19 + 3 * y >= 0, 19 + 3 * y == 49),
                    y == 10,
                ),
            )
        )
        checks.append(
            {
                "name": "algebraic_solution_unique",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved with kd.prove(): {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "algebraic_solution_unique",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the implication in kdrag: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the claimed solution y = 10.
    try:
        lhs = (19 + 3 * 10) ** 0.5
        passed = abs(lhs - 7.0) < 1e-12
        checks.append(
            {
                "name": "numerical_sanity_at_y_10",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"sqrt(19 + 3*10) = {lhs}, expected 7.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_at_y_10",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical evaluation failed: {type(e).__name__}: {e}",
            }
        )

    # A second checked fact: the derived equation 3y = 30 has the unique solution y = 10.
    try:
        y2 = Real("y2")
        thm2 = kd.prove(ForAll([y2], Implies(3 * y2 == 30, y2 == 10)))
        checks.append(
            {
                "name": "linear_equation_solution",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved with kd.prove(): {thm2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "linear_equation_solution",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove linear equation solution in kdrag: {type(e).__name__}: {e}",
            }
        )

    proved = proved and all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)