from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Ints, ForAll, Implies, And


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: derive that the line through B(7,-1) and C(-1,7)
    # can be written as y = -x + 6, hence m + b = 5.
    x, y = Ints("x y")
    try:
        # The concrete line equation is checked by proving the two given points satisfy it.
        thm = kd.prove(And((-1) == -(7) + 6, (7) == -(-1) + 6))
        checks.append({
            "name": "points_satisfy_line_y_equals_minus_x_plus_6",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "points_satisfy_line_y_equals_minus_x_plus_6",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # A second verified proof: if y = -x + 6, then m + b = 5.
    # We encode the concrete arithmetic identity as a theorem.
    try:
        thm2 = kd.prove((-1) + 6 == 5)
        checks.append({
            "name": "m_plus_b_equals_5_arithmetic",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "m_plus_b_equals_5_arithmetic",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at the concrete points.
    try:
        def line(xv):
            return -xv + 6

        ok = (line(7) == -1) and (line(-1) == 7)
        checks.append({
            "name": "numerical_point_check",
            "passed": ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Evaluated y = -x + 6 at x = 7 and x = -1; matched B(7,-1) and C(-1,7).",
        })
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_point_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)