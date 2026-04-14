from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, And, Not


# Problem: find the intersection of
#   s = 9 - 2t
#   t = 3s + 1
# and show it is (1, 4).


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    all_passed = True

    s = Int("s")
    t = Int("t")

    # Directly verify that (1,4) satisfies both equations.
    try:
        kd.prove(And(1 == 9 - 2 * 4, 4 == 3 * 1 + 1))
        checks.append({
            "name": "candidate_satisfies_system",
            "passed": True,
            "backend": "kdrag",
        })
    except Exception as e:
        checks.append({
            "name": "candidate_satisfies_system",
            "passed": False,
            "backend": "kdrag",
            "error": str(e),
        })
        all_passed = False

    # Verify uniqueness by showing the system forces s = 1 and t = 4.
    try:
        kd.prove(
            Not(
                And(
                    s == 9 - 2 * t,
                    t == 3 * s + 1,
                    Not(And(s == 1, t == 4)),
                )
            )
        )
        checks.append({
            "name": "unique_intersection",
            "passed": True,
            "backend": "kdrag",
        })
    except Exception as e:
        checks.append({
            "name": "unique_intersection",
            "passed": False,
            "backend": "kdrag",
            "error": str(e),
        })
        all_passed = False

    return {"passed": all_passed, "checks": checks}