from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies

from sympy import Integer


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: algebraic identity for the area change.
    # For any integer s and delta, (s-delta)(s+delta) = s^2 - delta^2.
    # Here s = 3491 and delta = 60, so the area decrease is 60^2 = 3600.
    try:
        s = Int("s")
        d = Int("d")
        thm = kd.prove(
            ForAll(
                [s, d],
                (s - d) * (s + d) == s * s - d * d,
            )
        )
        passed = True
        details = f"Certified identity proved by kdrag: {thm}"
    except Exception as e:
        passed = False
        proved = False
        details = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append(
        {
            "name": "algebraic_identity_for_area_change",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details,
        }
    )

    # Numerical sanity check at the concrete values from the problem.
    try:
        original = Integer(3491) ** 2
        new_area = Integer(3491 - 60) * Integer(3491 + 60)
        change = original - new_area
        passed = (change == 3600)
        if not passed:
            proved = False
        details = f"original={original}, new_area={new_area}, change={change}"
    except Exception as e:
        passed = False
        proved = False
        details = f"Numerical check failed: {type(e).__name__}: {e}"
    checks.append(
        {
            "name": "numerical_area_change",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details,
        }
    )

    # Direct symbolic computation using exact arithmetic.
    try:
        s = Integer(3491)
        d = Integer(60)
        symbolic_change = s**2 - (s - d) * (s + d)
        passed = (symbolic_change == 3600)
        if not passed:
            proved = False
        details = f"symbolic_change={symbolic_change}"
    except Exception as e:
        passed = False
        proved = False
        details = f"Symbolic computation failed: {type(e).__name__}: {e}"
    checks.append(
        {
            "name": "symbolic_exact_difference",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": details,
        }
    )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)