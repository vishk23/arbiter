from __future__ import annotations

from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import *
from sympy import Integer, Rational


def _check_kdrag_main() -> Dict[str, Any]:
    """
    Prove the core theorem over positive reals:
    If log_x w = 24, log_y w = 40, log_{xyz} w = 12,
    encoded as x^24=w, y^40=w, (xyz)^12=w, then z^60=w.
    Hence log_z w = 60.
    """
    x, y, z, w = Reals("x y z w")

    thm = ForAll(
        [x, y, z, w],
        Implies(
            And(
                x > 1,
                y > 1,
                z > 1,
                w > 0,
                x**24 == w,
                y**40 == w,
                (x * y * z) ** 12 == w,
            ),
            z**60 == w,
        ),
    )

    try:
        proof = kd.prove(thm)
        return {
            "name": "kdrag_core_power_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified with kd.prove: {proof}",
        }
    except Exception as e:
        return {
            "name": "kdrag_core_power_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_kdrag_uniqueness_of_log_value() -> Dict[str, Any]:
    """
    Prove that for any z>1 and w>0, if z^60=w and z^t=w then t=60.
    This justifies that log_z w is uniquely 60.
    """
    z, w, t = Reals("z w t")

    thm = ForAll(
        [z, w, t],
        Implies(
            And(z > 1, w > 0, z**60 == w, z**t == w),
            t == 60,
        ),
    )

    try:
        proof = kd.prove(thm)
        return {
            "name": "kdrag_log_value_unique",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified uniqueness of exponent with kd.prove: {proof}",
        }
    except Exception as e:
        return {
            "name": "kdrag_log_value_unique",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_numerical_sanity() -> Dict[str, Any]:
    """
    Concrete example satisfying the hypotheses:
    choose w = 2^120, then x = 2^5, y = 2^3, z = 2^2.
    Check the given logs and the target log_z w = 60.
    """
    w = Integer(2) ** 120
    x = Integer(2) ** 5
    y = Integer(2) ** 3
    z = Integer(2) ** 2

    passed = (
        x ** 24 == w
        and y ** 40 == w
        and (x * y * z) ** 12 == w
        and z ** 60 == w
    )

    details = (
        f"Concrete witness: x={x}, y={y}, z={z}, w=2^120. "
        f"Checks: x^24=w -> {x**24 == w}, y^40=w -> {y**40 == w}, "
        f"(xyz)^12=w -> {(x*y*z)**12 == w}, z^60=w -> {z**60 == w}."
    )

    return {
        "name": "numerical_sanity_example",
        "passed": bool(passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_check_kdrag_main())
    checks.append(_check_kdrag_uniqueness_of_log_value())
    checks.append(_check_numerical_sanity())

    proved = all(ch.get("passed", False) for ch in checks) and any(
        ch.get("backend") in {"kdrag", "sympy"} and ch.get("passed", False)
        for ch in checks
    )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2, default=str))