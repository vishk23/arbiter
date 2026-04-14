import math
from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, sqrt, Rational, simplify, nsimplify, N


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Check 1: From the hypotheses, the fractional-part condition implies
    # a^2 - 2 = 1/a, equivalently a^3 - 2a - 1 = 0, for all positive reals a
    # with 2 < a^2 < 3 and frac(1/a) = frac(a^2).
    try:
        a = Real("a")
        thm = ForAll(
            [a],
            Implies(
                And(a > 0, a * a > 2, a * a < 3, a * a - 2 == 1 / a),
                a * a * a - 2 * a - 1 == 0,
            ),
        )
        pf = kd.prove(thm)
        checks.append(
            {
                "name": "kdrag_cubic_from_rearrangement",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(pf),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_cubic_from_rearrangement",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: The positive solution of a^2 - a - 1 = 0 is phi, and it also
    # satisfies a^3 - 2a - 1 = 0. This is a rigorous symbolic identity check.
    try:
        phi = (1 + sqrt(5)) / 2
        expr = simplify(phi**3 - 2 * phi - 1)
        passed = expr == 0
        checks.append(
            {
                "name": "sympy_phi_satisfies_cubic",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"simplify(((1+sqrt(5))/2)^3 - 2*((1+sqrt(5))/2) - 1) = {expr}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sympy_phi_satisfies_cubic",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Symbolic verification failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Exact symbolic evaluation of the requested expression at phi.
    try:
        phi = (1 + sqrt(5)) / 2
        target_expr = simplify(phi**12 - 144 / phi)
        passed = target_expr == 233
        checks.append(
            {
                "name": "sympy_exact_final_value",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"simplify(phi^12 - 144/phi) = {target_expr}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sympy_exact_final_value",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Exact symbolic evaluation failed: {type(e).__name__}: {e}",
            }
        )

    # Check 4: Numerical sanity check that phi satisfies the original fractional-part condition.
    try:
        phi_f = (1 + math.sqrt(5)) / 2
        frac_inv = phi_f ** -1 - math.floor(phi_f ** -1)
        frac_sq = phi_f ** 2 - math.floor(phi_f ** 2)
        same_frac = abs(frac_inv - frac_sq) < 1e-12
        in_range = 2 < phi_f ** 2 < 3
        val = phi_f ** 12 - 144 / phi_f
        near_233 = abs(val - 233.0) < 1e-9
        passed = same_frac and in_range and near_233
        checks.append(
            {
                "name": "numerical_sanity_original_conditions_and_value",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": (
                    f"phi≈{phi_f:.15f}, frac(1/phi)≈{frac_inv:.15f}, "
                    f"frac(phi^2)≈{frac_sq:.15f}, phi^2≈{phi_f**2:.15f}, "
                    f"phi^12-144/phi≈{val:.12f}"
                ),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_original_conditions_and_value",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    # Check 5: Uniqueness on the stated interval via kdrag.
    # Any positive real a with 2 < a^2 < 3 and a^3 - 2a - 1 = 0 must satisfy a^2 - a - 1 = 0.
    try:
        a = Real("a")
        thm2 = ForAll(
            [a],
            Implies(
                And(a > 0, a * a > 2, a * a < 3, a * a * a - 2 * a - 1 == 0),
                a * a - a - 1 == 0,
            ),
        )
        pf2 = kd.prove(thm2)
        checks.append(
            {
                "name": "kdrag_reduce_cubic_to_quadratic_on_interval",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(pf2),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_reduce_cubic_to_quadratic_on_interval",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2))