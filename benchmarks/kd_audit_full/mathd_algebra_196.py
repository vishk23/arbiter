from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: the solutions to |2 - x| = 3 are exactly x = -1 and x = 5,
    # and their sum is 4.
    x = Real("x")
    sol_sum = RealVal(4)
    try:
        thm = kd.prove(
            ForAll(
                [x],
                Implies(
                    Abs(RealVal(2) - x) == RealVal(3),
                    Or(x == RealVal(-1), x == RealVal(5)),
                ),
            )
        )
        check1 = {
            "name": "absolute_value_solutions_characterization",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        }
        checks.append(check1)
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "absolute_value_solutions_characterization",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove solution characterization: {type(e).__name__}: {e}",
            }
        )

    # Prove the sum of the two solutions is 4.
    try:
        x1, x2 = Reals("x1 x2")
        thm2 = kd.prove(
            ForAll(
                [x1, x2],
                Implies(
                    And(x1 == RealVal(-1), x2 == RealVal(5)),
                    x1 + x2 == RealVal(4),
                ),
            )
        )
        checks.append(
            {
                "name": "sum_of_solutions_is_four",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sum_of_solutions_is_four",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove sum claim: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the two concrete solutions.
    try:
        import math

        vals = [-1.0, 5.0]
        residuals = [abs(2 - v) - 3 for v in vals]
        sum_val = sum(vals)
        numerical_passed = all(abs(r) < 1e-12 for r in residuals) and abs(sum_val - 4.0) < 1e-12
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": numerical_passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"residuals={residuals}, sum={sum_val}",
            }
        )
        proved = proved and numerical_passed
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
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