from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And



def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Verified theorem: if two real numbers sum to 25 and differ by 11,
    # then the larger one is 18.
    try:
        x = Real("x")
        y = Real("y")
        thm = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(x + y == 25, x - y == 11),
                    x == 18,
                ),
            )
        )
        checks.append(
            {
                "name": "larger_number_is_18_proof",
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
                "name": "larger_number_is_18_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete solution x=18, y=7.
    try:
        x_val = 18
        y_val = 7
        passed = (x_val + y_val == 25) and (x_val - y_val == 11) and (x_val == 18)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Checked x=18, y=7: sum={x_val + y_val}, diff={x_val - y_val}, larger={x_val}.",
            }
        )
        proved = proved and bool(passed)
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