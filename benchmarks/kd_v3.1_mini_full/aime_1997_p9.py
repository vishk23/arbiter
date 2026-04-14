from __future__ import annotations

from fractions import Fraction
import math

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Real, Int, ForAll, Implies, And, Or, Not
except Exception:  # pragma: no cover
    kd = None


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: formal proof that the equation on fractional parts forces a^3 - 2a - 1 = 0.
    # We encode the key algebraic step with kdrag as a certificate-bearing proof:
    # if 2 < a^2 < 3 and frac(a^{-1}) = frac(a^2), then since a^{-1} < 1 and a^2 in (2,3),
    # we have a^{-1} = a^2 - 2, hence a^3 - 2a - 1 = 0.
    try:
        if kd is None:
            raise RuntimeError("kdrag unavailable")

        a = Real("a")
        ainv = Real("ainv")
        # Abstractly prove the algebraic consequence from the equation ainv = a^2 - 2.
        # This is the core Z3-encodable implication we can certify.
        thm = kd.prove(
            ForAll(
                [a, ainv],
                Implies(
                    And(a > 0, ainv == 1 / a, a * a > 2, a * a < 3, ainv == a * a - 2),
                    a * a * a - 2 * a - 1 == 0,
                ),
            )
        )
        checks.append(
            {
                "name": "algebraic_reduction_to_cubic",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kd.prove(): {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "algebraic_reduction_to_cubic",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Could not certify the implication with kdrag: {e}",
            }
        )

    # Check 2: symbolic verification of the exact polynomial root and target value.
    # From a^3 - 2a - 1 = 0, the positive root is the golden ratio phi.
    try:
        x = sp.Symbol("x", positive=True)
        phi = (1 + sp.sqrt(5)) / 2
        poly_check = sp.simplify(phi ** 3 - 2 * phi - 1)
        target = sp.simplify(phi ** 12 - 144 * phi ** (-1))
        # Rigorous symbolic simplification in SymPy.
        passed = sp.simplify(poly_check) == 0 and sp.simplify(target - 233) == 0
        if not passed:
            proved = False
        checks.append(
            {
                "name": "symbolic_evaluation_at_golden_ratio",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"phi^3 - 2phi - 1 = {sp.simplify(poly_check)}; phi^12 - 144/phi = {sp.simplify(target)}.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "symbolic_evaluation_at_golden_ratio",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic verification failed: {e}",
            }
        )

    # Check 3: numerical sanity check at the concrete value phi.
    try:
        phi_num = (1 + math.sqrt(5.0)) / 2.0
        val = phi_num ** 12 - 144.0 / phi_num
        passed = abs(val - 233.0) < 1e-9
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed value {val:.12f} at phi; expected 233.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical evaluation failed: {e}",
            }
        )

    # Check 4: exact algebraic reduction from phi^2 = phi + 1 and phi^12 - 144/phi = 233.
    try:
        phi = sp.Symbol("phi")
        # Use the minimal polynomial certificate-like symbolic identity for phi.
        expr = sp.expand((sp.Rational(1, 2) * (3 + sp.sqrt(5))) ** 6 - 144 * (2 / (1 + sp.sqrt(5))))
        simplified = sp.simplify(expr)
        passed = simplified == 233
        if not passed:
            proved = False
        checks.append(
            {
                "name": "exact_closed_form_simplification",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Expanded exact expression simplifies to {simplified}.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "exact_closed_form_simplification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Closed-form simplification failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)