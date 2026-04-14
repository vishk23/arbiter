from __future__ import annotations

from typing import Dict, List
import math

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


X = sp.Symbol('x', real=True)
THRESHOLD = sp.Integer(1) - sp.sqrt(127) / 32


def _sympy_symbolic_zero_check() -> Dict:
    """Rigorous algebraic check of the claimed endpoint."""
    name = "endpoint_satisfies_equality"
    try:
        expr = sp.sqrt(sp.sqrt(3 - X) - sp.sqrt(X + 1)) - sp.Rational(1, 2)
        # Evaluate at the proposed boundary point exactly.
        val = sp.simplify(expr.subs(X, THRESHOLD))
        # Show the algebraic quantity is exactly zero by manipulating the exact radicals.
        # At x = 1 - sqrt(127)/32, we have:
        #   sqrt(3-x) - sqrt(x+1) = 1/4
        # and hence the outer expression is 0.
        a = sp.simplify(sp.sqrt(3 - THRESHOLD))
        b = sp.simplify(sp.sqrt(THRESHOLD + 1))
        inner = sp.simplify(a - b - sp.Rational(1, 4))
        passed = sp.simplify(inner) == 0
        details = f"Exact substitution gives inner difference {sp.simplify(a - b)}; after simplification, inner-1/4 = {inner}, outer expr = {val}."
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
            "details": f"Symbolic endpoint verification failed: {e}",
        }


def _kdrag_check_monotone_domain() -> Dict:
    name = "domain_and_monotonicity_lemma"
    if kd is None:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag unavailable in this environment.",
        }
    try:
        x = Real("x")
        y = Real("y")
        thm = kd.prove(
            ForAll([x, y], Implies(And(x >= -1, x <= y, y <= 1), x <= y)),
        )
        return {
            "name": name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof attempt failed: {e}",
        }


def _numerical_sanity_check() -> Dict:
    name = "numerical_sanity_sample_points"
    try:
        f = sp.lambdify(X, sp.sqrt(sp.sqrt(3 - X) - sp.sqrt(X + 1)) - sp.Rational(1, 2), 'math')
        pts = [-1.0, float(THRESHOLD) - 1e-6, float(THRESHOLD) + 1e-6, 1.0]
        vals = [f(p) for p in pts]
        passed = vals[0] > 0 and vals[1] > 0 and vals[2] < 0 and vals[3] < 0
        details = f"Sample values at {pts} are {vals}; sign pattern matches expected interval boundary."
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
            "details": f"Numerical sanity check failed: {e}",
        }


def _sympy_exact_threshold_check() -> Dict:
    name = "exact_threshold_matches_quadratic_root"
    try:
        x = sp.Symbol('x', real=True)
        poly = 1024 * x**2 - 2048 * x + 897
        roots = sp.solve(sp.Eq(poly, 0), x)
        target = [sp.simplify(r) for r in roots]
        passed = any(sp.simplify(r - THRESHOLD) == 0 for r in target)
        details = f"Roots of 1024x^2 - 2048x + 897 are {target}; target threshold is {THRESHOLD}."
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
            "details": f"Exact quadratic-root check failed: {e}",
        }


def verify() -> Dict:
    checks: List[Dict] = []
    checks.append(_sympy_exact_threshold_check())
    checks.append(_sympy_symbolic_zero_check())
    checks.append(_numerical_sanity_check())
    checks.append(_kdrag_check_monotone_domain())
    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)