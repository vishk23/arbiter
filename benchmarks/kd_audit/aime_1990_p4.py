from __future__ import annotations

from typing import Any, Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Real, Int, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


x = sp.Symbol("x", real=True)
a = sp.Symbol("a", real=True)


def _numerical_residual(val: float) -> float:
    expr = 1 / (val**2 - 10 * val - 29) + 1 / (val**2 - 10 * val - 45) - 2 / (val**2 - 10 * val - 69)
    return float(sp.N(expr, 30))


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Check 1: symbolic derivation that a=10 implies x=13 or x=-3, with positive solution 13.
    try:
        eq_a = sp.expand((a - 16) * (a - 40) + a * (a - 40) - 2 * a * (a - 16))
        reduced = sp.factor(eq_a)
        # For the target equation, the numerator simplifies to 64*(10-a), hence a=10.
        symbolic_ok = sp.expand(eq_a) == sp.expand(-64 * a + 640)
        # Substitute a=10 into x^2-10x-29 = 10
        roots_poly = sp.factor(x**2 - 10 * x - 39)
        symbolic_ok = symbolic_ok and roots_poly == (x - 13) * (x + 3)
        checks.append({
            "name": "symbolic_reduction_and_root_extraction",
            "passed": bool(symbolic_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Reduced numerator: {sp.expand(eq_a)}; factorization: {roots_poly}.",
        })
    except Exception as e:
        checks.append({
            "name": "symbolic_reduction_and_root_extraction",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy failure: {e}",
        })

    # Check 2: verified proof in kdrag for the reduced algebraic implication.
    if kd is not None:
        try:
            ar = Real("ar")
            thm = kd.prove(
                ForAll([
                    ar
                ], Implies(
                    And(1 / ar + 1 / (ar - 16) - 2 / (ar - 40) == 0, ar != 0, ar != 16, ar != 40),
                    ar == 10,
                ))
            )
            passed = thm is not None
            details = "kd.prove succeeded for the reduced rational equation implying a=10."
            checks.append({
                "name": "kdrag_certificate_for_reduced_equation",
                "passed": passed,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": details,
            })
        except Exception as e:
            checks.append({
                "name": "kdrag_certificate_for_reduced_equation",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof could not be constructed: {e}",
            })
    else:
        checks.append({
            "name": "kdrag_certificate_for_reduced_equation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment.",
        })

    # Check 3: numerical sanity check at the claimed positive solution x=13.
    try:
        residual_13 = _numerical_residual(13.0)
        passed = abs(residual_13) < 1e-12
        checks.append({
            "name": "numerical_sanity_at_x_13",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Residual at x=13 is {residual_13:.3e}.",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_at_x_13",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}",
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)