from __future__ import annotations

from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def _check_kdrag_theorem() -> Dict[str, Any]:
    """Verified proof that the logarithm conditions imply log_z(w) = 60."""
    x = Real("x")
    y = Real("y")
    z = Real("z")
    w = Real("w")

    # Encode the logarithmic assumptions as exponential equalities.
    # Since x,y,z > 1 and w > 0, these are valid log-base relations.
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
        prf = kd.prove(thm)
        return {
            "name": "main_log_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {prf}",
        }
    except Exception as e:
        return {
            "name": "main_log_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        }


def _check_numerical_sanity() -> Dict[str, Any]:
    """Concrete sanity check using the derived ratio 24:40:12."""
    # Choose w=1 and consistent bases x=1, y=1, z=1 are invalid; instead use a
    # direct algebraic consistency check on exponents from the implied equations:
    # 24 log x(w) = 40 log y(w) = 12 log(xyz)(w). The derivation yields log_z(w)=60.
    # Use explicit numbers satisfying the exponent relations:
    # Let w = 2^120, x = 2^5, y = 2^3, z = 2^2.
    import math

    w = 2.0 ** 120
    x = 2.0 ** 5
    y = 2.0 ** 3
    z = 2.0 ** 2
    c1 = abs(math.log(w, x) - 24.0) < 1e-9
    c2 = abs(math.log(w, y) - 40.0) < 1e-9
    c3 = abs(math.log(w, x * y * z) - 12.0) < 1e-9
    c4 = abs(math.log(w, z) - 60.0) < 1e-9
    passed = c1 and c2 and c3 and c4
    return {
        "name": "numerical_sanity_example",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": (
            f"Checks: log_x(w)=24 -> {c1}, log_y(w)=40 -> {c2}, "
            f"log_(xyz)(w)=12 -> {c3}, log_z(w)=60 -> {c4}."
        ),
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_check_kdrag_theorem())
    checks.append(_check_numerical_sanity())
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)