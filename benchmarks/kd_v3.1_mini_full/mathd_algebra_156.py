from __future__ import annotations

from typing import Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Ints, Int, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


def _check_kdrag_factorization() -> dict:
    name = "quartic_factorization_to_u_quadratic"
    if kd is None:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in the runtime, so the proof could not be constructed.",
        }

    try:
        u = Int("u")
        # Algebraic core: if u satisfies u^2 - 5u + 6 = 0, then (u-2)(u-3)=0.
        thm = kd.prove(
            ForAll([u], Implies(u * u - 5 * u + 6 == 0, (u - 2) * (u - 3) == 0))
        )
        return {
            "name": name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by kdrag: {thm}",
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_sympy_solution_set() -> dict:
    name = "solve_for_x_squared_values"
    x, u = sp.symbols("x u")
    try:
        sol_u = sp.solve(sp.Eq(u**2 - 5 * u + 6, 0), u)
        passed = set(sol_u) == {sp.Integer(2), sp.Integer(3)}
        details = f"Solved u^2 - 5u + 6 = 0, obtaining {sol_u}."
        return {
            "name": name,
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": details,
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve failed: {type(e).__name__}: {e}",
        }


def _check_numerical_sanity() -> dict:
    name = "numerical_intersection_sanity"
    try:
        vals = [sp.sqrt(2), -sp.sqrt(2), sp.sqrt(3), -sp.sqrt(3)]
        passed = True
        residuals = []
        for v in vals:
            r = sp.N(v**4 - (5 * v**2 - 6), 30)
            residuals.append(r)
            passed = passed and abs(complex(r)) < 1e-20
        details = f"Evaluated residual x^4-(5x^2-6) at ±sqrt(2), ±sqrt(3): {residuals}."
        return {
            "name": name,
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details,
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
        }


def _check_answer_difference() -> dict:
    name = "m_minus_n_equals_one"
    try:
        m = sp.Integer(3)
        n = sp.Integer(2)
        diff = sp.simplify(m - n)
        passed = diff == 1
        return {
            "name": name,
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"From u = 3, 2 we get m = 3, n = 2, so m-n = {diff}.",
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Final arithmetic check failed: {type(e).__name__}: {e}",
        }


def verify() -> Dict[str, object]:
    checks = [
        _check_kdrag_factorization(),
        _check_sympy_solution_set(),
        _check_numerical_sanity(),
        _check_answer_difference(),
    ]
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)