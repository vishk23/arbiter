from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, And, Implies, ForAll, Solver, sat


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Verified proof: the unique intersection point (x, y) of
    # 3y = x and 2x + 5y = 11 is (3, 1), hence x + y = 4.
    x = Int("x")
    y = Int("y")
    try:
        # Prove that any integer solution of the system must satisfy x + y = 4.
        thm = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(x == 3 * y, 2 * x + 5 * y == 11),
                    x + y == 4,
                ),
            )
        )
        checks.append(
            {
                "name": "intersection_sum_is_4_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned a Proof object: {thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "intersection_sum_is_4_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete point (3,1).
    try:
        x0, y0 = 3, 1
        passed = (3 * y0 == x0) and (2 * x0 + 5 * y0 == 11) and (x0 + y0 == 4)
        checks.append(
            {
                "name": "numerical_sanity_at_point_3_1",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Checked (x,y)=({x0},{y0}): 3y=x, 2x+5y=11, and x+y=4 all evaluate to True.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_at_point_3_1",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)