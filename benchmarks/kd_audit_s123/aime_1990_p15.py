from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *

from sympy import Rational, Symbol
from sympy import minimal_polynomial


def verify() -> dict:
    checks: List[Dict[str, object]] = []
    proved = True

    # Verified proof 1: derive the target value by algebraic elimination in kdrag.
    a, b, x, y = Reals("a b x y")
    s1 = a * x + b * y
    s2 = a * x**2 + b * y**2
    s3 = a * x**3 + b * y**3
    s4 = a * x**4 + b * y**4
    s5 = a * x**5 + b * y**5
    S = x + y
    P = x * y

    try:
        thm = kd.prove(
            Implies(
                And(s1 == 3, s2 == 7, s3 == 16, s4 == 42),
                s5 == 20,
            )
        )
        checks.append(
            {
                "name": "algebraic_elimination_kdrag",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded with proof object: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "algebraic_elimination_kdrag",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # SymPy symbolic check: the computed value is exactly 20.
    try:
        expr = Rational(42) * Rational(-14) + Rational(38) * Rational(16)
        z = Symbol("z")
        mp = minimal_polynomial(expr - Rational(20), z)
        sympy_passed = mp == z
        checks.append(
            {
                "name": "symbolic_zero_for_target_value",
                "passed": bool(sympy_passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"minimal_polynomial(expr - 20, z) == z evaluated to {mp == z}; expr={expr}",
            }
        )
        if not sympy_passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "symbolic_zero_for_target_value",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check with concrete values satisfying the derived S and P relations.
    # Choose x,y as roots of t^2 + 14 t - 38 = 0, then S=-14 and P=-38.
    try:
        # One concrete root pair and coefficients chosen to satisfy the system.
        # Let x,y be roots; define a,b from the linear system using the first two equations.
        import math

        disc = 14 * 14 + 4 * 38
        r1 = (-14 + math.sqrt(disc)) / 2.0
        r2 = (-14 - math.sqrt(disc)) / 2.0
        # Solve for a,b from a*x + b*y = 3 and a*x^2 + b*y^2 = 7.
        det = r1 * (r2**2) - r2 * (r1**2)
        a_num = 3 * (r2**2) - 7 * r2
        b_num = 7 * r1 - 3 * (r1**2)
        a_val = a_num / det
        b_val = b_num / det
        val = a_val * (r1**5) + b_val * (r2**5)
        num_passed = abs(val - 20.0) < 1e-6
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(num_passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Using concrete roots x={r1}, y={r2}, computed ax^5+by^5={val}",
            }
        )
        if not num_passed:
            proved = False
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