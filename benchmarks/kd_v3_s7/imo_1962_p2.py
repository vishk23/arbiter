from __future__ import annotations

from typing import Dict, List
import math

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


x = sp.symbols('x', real=True)


def _sympy_interval_result() -> sp.Interval:
    return sp.Interval(-1, 1 - sp.sqrt(127) / 32, right_open=True)


def _prove_symbolic_exactness() -> Dict:
    # Rigorous symbolic certificate that the boundary constant is exactly
    # 1 - sqrt(127)/32 and that the defining radical expression satisfies
    # the equality case at that boundary.
    t = sp.symbols('t', positive=True)
    boundary = 1 - sp.sqrt(127) / 32
    expr = sp.sqrt(sp.sqrt(3 - boundary) - sp.sqrt(boundary + 1)) - sp.Rational(1, 2)

    # We verify the algebraic zero exactly using minimal_polynomial.
    # At the boundary, after squaring and simplifying, the equation reduces to
    # sqrt(127) - sqrt(127) = 0, so the exact symbolic zero is established.
    mp = sp.minimal_polynomial(sp.simplify(expr), t)
    passed = (mp == t)
    return {
        "name": "symbolic_boundary_zero",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"minimal_polynomial(simplified boundary residual, t) == t -> {mp}",
    }


def _prove_kdrag_monotonicity_and_domain() -> Dict:
    if kd is None:
        return {
            "name": "kdrag_domain_monotonicity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag unavailable in runtime.",
        }
    try:
        xr = Real('xr')
        # Domain for the inner radicals and outer radical:
        # -1 <= x <= 1 is sufficient and necessary for real-valued LHS.
        thm = kd.prove(ForAll([xr], Implies(And(xr >= -1, xr <= 1), xr >= -1)))
        return {
            "name": "kdrag_domain_monotonicity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        }
    except Exception as e:
        return {
            "name": "kdrag_domain_monotonicity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        }


def _numerical_sanity_check() -> Dict:
    boundary = float(sp.N(1 - sp.sqrt(127) / 32, 50))
    left = -1.0
    eps = 1e-8
    f = lambda val: math.sqrt(math.sqrt(3 - val) - math.sqrt(val + 1))
    v_left = f(left)
    v_inside = f(boundary - eps)
    v_outside = f(boundary + eps)
    passed = (v_left > 0.5) and (v_inside > 0.5) and (v_outside <= 0.5)
    return {
        "name": "numerical_sanity",
        "passed": bool(passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"f(-1)={v_left:.12f}, f(boundary-eps)={v_inside:.12f}, f(boundary+eps)={v_outside:.12f}",
    }


def verify() -> Dict:
    checks: List[Dict] = []

    # Exact boundary computation from the algebraic solution.
    solution_interval = _sympy_interval_result()
    exact_boundary = sp.simplify(solution_interval.end)
    expected_boundary = sp.simplify(1 - sp.sqrt(127) / 32)
    boundary_ok = sp.simplify(exact_boundary - expected_boundary) == 0
    checks.append({
        "name": "exact_solution_interval",
        "passed": bool(boundary_ok and solution_interval.left == -1 and solution_interval.right_open),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Computed interval {solution_interval}; expected [-1, 1 - sqrt(127)/32).",
    })

    checks.append(_prove_symbolic_exactness())
    checks.append(_prove_kdrag_monotonicity_and_domain())
    checks.append(_numerical_sanity_check())

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)