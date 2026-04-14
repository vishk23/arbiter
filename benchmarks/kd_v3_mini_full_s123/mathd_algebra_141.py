from __future__ import annotations

import math
from typing import Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Ints, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


def _check_kdrag_proof() -> Dict:
    name = "rectangle_sides_imply_diagonal_squared_369"
    if kd is None:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in the runtime environment, so no formal certificate could be produced.",
        }

    try:
        a, b = Ints("a b")
        # If a and b are rectangle side lengths satisfying area 180 and perimeter 54,
        # then (a+b)^2 - 2ab = 369, so a^2 + b^2 = 369.
        thm = kd.prove(
            ForAll(
                [a, b],
                Implies(
                    And(a * b == 180, 2 * (a + b) == 54),
                    a * a + b * b == 369,
                ),
            )
        )
        return {
            "name": name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded and returned a proof object: {thm}",
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Formal proof attempt failed in kdrag: {type(e).__name__}: {e}",
        }


def _check_symbolic_computation() -> Dict:
    name = "symbolic_diagonal_squared_computation"
    s = sp.Integer(27)
    p = sp.Integer(180)
    diag_sq = sp.expand(s ** 2 - 2 * p)
    passed = diag_sq == 369
    return {
        "name": name,
        "passed": passed,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"Computed (a+b)^2 - 2ab = 27^2 - 2*180 = {diag_sq}.",
    }


def _check_numerical_sanity() -> Dict:
    name = "numerical_sanity_for_sides_12_15"
    a = 12
    b = 15
    area = a * b
    perimeter = 2 * (a + b)
    diag_sq = a * a + b * b
    passed = (area == 180) and (perimeter == 54) and (diag_sq == 369)
    return {
        "name": name,
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"With a=12 and b=15: area={area}, perimeter={perimeter}, diagonal^2={diag_sq}.",
    }


def verify() -> Dict:
    checks: List[Dict] = [
        _check_kdrag_proof(),
        _check_symbolic_computation(),
        _check_numerical_sanity(),
    ]
    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)