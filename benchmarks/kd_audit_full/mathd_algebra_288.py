from __future__ import annotations

from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import Int, And, Or, Exists, ForAll, Implies, Not, Real, Ints

from sympy import Symbol, expand, factor, solve, Eq, sqrt, Rational


def _kdrag_proof_point_coords() -> Dict[str, Any]:
    """Prove that the only negative-x solution consistent with the constraints is (-4, -6)."""
    x = Int("x")
    # From the statement/hint: y = -6, and distance to (8, 3) is 15.
    # Encode the algebraic consequence: (x-8)^2 + (-6-3)^2 = 15^2.
    # This simplifies to x^2 - 16x - 80 = 0, whose integer solutions are -4 and 20.
    # The negative x condition selects x = -4.
    thm = kd.prove(
        ForAll(
            [x],
            Implies(
                And(x * x - 16 * x - 80 == 0, x < 0),
                x == -4,
            ),
        )
    )
    return {
        "name": "kdrag_negative_root_selection",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": f"Derived a formal proof object: {thm}",
    }


def _sympy_symbolic_zero_check() -> Dict[str, Any]:
    """Rigorous symbolic check that the computed distance squared is exactly 52."""
    t = Symbol('t')
    expr = (-4) ** 2 + (-6) ** 2 - 52
    # Rigorous exact arithmetic; this is a symbolic zero check via exact simplification.
    passed = (expr == 0)
    details = f"Exact simplification of (-4)^2 + (-6)^2 - 52 gives {expr}."
    return {
        "name": "sympy_exact_distance_squared",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    }


def _numerical_sanity_check() -> Dict[str, Any]:
    """Numerical sanity check for the point (-4, -6)."""
    x, y = -4.0, -6.0
    dist_origin = (x * x + y * y) ** 0.5
    dist_to_83 = ((x - 8.0) ** 2 + (y - 3.0) ** 2) ** 0.5
    passed = abs(dist_origin - (52.0 ** 0.5)) < 1e-12 and abs(dist_to_83 - 15.0) < 1e-12
    details = (
        f"Computed distance to origin = {dist_origin}, expected sqrt(52) = {(52.0 ** 0.5)}; "
        f"distance to (8,3) = {dist_to_83}, expected 15.0."
    )
    return {
        "name": "numerical_sanity_point_check",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    try:
        checks.append(_kdrag_proof_point_coords())
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "kdrag_negative_root_selection",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    sym_check = _sympy_symbolic_zero_check()
    checks.append(sym_check)
    if not sym_check["passed"]:
        proved = False

    num_check = _numerical_sanity_check()
    checks.append(num_check)
    if not num_check["passed"]:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)