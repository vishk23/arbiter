from __future__ import annotations

from typing import Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Check 1: Verified symbolic proof using SymPy minimal polynomial.
    # Let k = log_2(x). Then k satisfies k + 4/k = 6, hence k^2 - 6k + 4 = 0.
    # The target expression is (log_2(x/y))^2 = (k - 4/k)^2 = (2k - 6)^2.
    # We prove this is always 20 by showing the algebraic expression is exactly 20
    # for either root of the quadratic, and certify via minimal_polynomial.
    try:
        k = sp.Symbol('k')
        poly = k**2 - 6*k + 4
        roots = sp.solve(sp.Eq(poly, 0), k)
        exprs = [sp.simplify((r - 4/r)**2) for r in roots]
        sympy_ok = all(sp.simplify(e - 20) == 0 for e in exprs)
        checks.append({
            "name": "symbolic_quadratic_solution_yields_20",
            "passed": bool(sympy_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Quadratic roots for k are {roots}; evaluating (k-4/k)^2 gives {exprs}, all simplifying to 20.",
        })
        proved = proved and sympy_ok
    except Exception as e:
        checks.append({
            "name": "symbolic_quadratic_solution_yields_20",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic verification failed: {e}",
        })
        proved = False

    # Check 2: Numerical sanity check at a concrete valid solution branch.
    try:
        sqrt5 = sp.sqrt(5)
        k_val = 3 + sqrt5
        target = sp.N((k_val - 4/k_val)**2, 30)
        num_ok = abs(float(target) - 20.0) < 1e-12
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Using k = 3 + sqrt(5), computed (k - 4/k)^2 ≈ {target}.",
        })
        proved = proved and num_ok
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {e}",
        })
        proved = False

    # Check 3: Optional kdrag proof of the algebraic relation on reals.
    # We encode the key derivation: if a > 0 and a + 4/a = 6, then (a - 4/a)^2 = 20.
    # This is a pure algebraic consequence, suitable for Z3.
    if kd is not None:
        try:
            a = Real('a')
            thm = kd.prove(ForAll([a], Implies(And(a != 0, a + 4 / a == 6), (a - 4 / a) * (a - 4 / a) == 20)))
            checks.append({
                "name": "kdrag_algebraic_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm}",
            })
        except Exception as e:
            checks.append({
                "name": "kdrag_algebraic_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            })
            proved = False
    else:
        checks.append({
            "name": "kdrag_algebraic_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment.",
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)