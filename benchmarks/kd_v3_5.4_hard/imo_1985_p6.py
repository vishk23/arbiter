import math
from typing import List, Dict, Any

import kdrag as kd
from kdrag.smt import *
from sympy import symbols, sqrt, simplify, Rational, minimal_polynomial


def _check_kdrag_basic_order_trichotomy() -> Dict[str, Any]:
    x = Real("x")
    try:
        pf = kd.prove(ForAll([x], Or(x < 0, x == 0, x > 0)))
        return {
            "name": "kdrag_real_trichotomy",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        }
    except Exception as e:
        return {
            "name": "kdrag_real_trichotomy",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag failed: {type(e).__name__}: {e}",
        }


def _check_kdrag_monotone_uniqueness_step() -> Dict[str, Any]:
    a, b, n = Reals("a b n")
    try:
        thm = ForAll(
            [a, b, n],
            Implies(
                And(n >= 1, a > 1 - 1 / n, a < 1, b > 1 - 1 / n, b < 1, b >= a),
                b * (b + 1 / n) - a * (a + 1 / n) >= b - a,
            ),
        )
        pf = kd.prove(thm)
        return {
            "name": "kdrag_difference_growth_step",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        }
    except Exception as e:
        return {
            "name": "kdrag_difference_growth_step",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag failed: {type(e).__name__}: {e}",
        }


def _check_sympy_inverse_formula() -> Dict[str, Any]:
    t = symbols("t", positive=True)
    n = symbols("n", positive=True)
    xinv = (-1 / n + sqrt(1 / n**2 + 4 * t)) / 2
    expr = simplify(xinv * (xinv + 1 / n) - t)
    z = symbols("z")
    try:
        mp = minimal_polynomial(expr, z)
        passed = (mp == z)
        return {
            "name": "sympy_inverse_branch_exact",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial of inverse-substitution residual is {mp}",
        }
    except Exception as e:
        return {
            "name": "sympy_inverse_branch_exact",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy failed: {type(e).__name__}: {e}",
        }


def _iterate(x1: float, N: int = 30) -> List[float]:
    xs = [x1]
    x = x1
    for n in range(1, N):
        x = x * (x + 1.0 / n)
        xs.append(x)
    return xs


def _predicate(xs: List[float]) -> bool:
    for n in range(len(xs) - 1):
        if not (0.0 < xs[n] < xs[n + 1] < 1.0):
            return False
    return True


def _search_unique_initial(N: int = 25, iters: int = 80) -> float:
    lo, hi = 0.0, 1.0
    for _ in range(iters):
        mid = (lo + hi) / 2.0
        xs = _iterate(mid, N)
        ok = True
        for n in range(N - 1):
            if xs[n + 1] >= 1.0:
                ok = False
                hi = mid
                break
            if xs[n + 1] <= xs[n]:
                ok = False
                lo = mid
                break
        if ok:
            lo = mid
    return (lo + hi) / 2.0


def _check_numerical_sanity() -> Dict[str, Any]:
    try:
        x1 = _search_unique_initial()
        xs = _iterate(x1, 20)
        ok = _predicate(xs)
        details = f"approx unique x1 ~ {x1:.15f}; first 8 terms: {[round(v, 12) for v in xs[:8]]}"
        return {
            "name": "numerical_sanity_candidate",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details,
        }
    except Exception as e:
        return {
            "name": "numerical_sanity_candidate",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical check failed: {type(e).__name__}: {e}",
        }


def _check_problem_status_explanation() -> Dict[str, Any]:
    details = (
        "The IMO statement is an existence-and-uniqueness theorem over an infinite sequence. "
        "This module verifies rigorously several key components used in the standard proof: "
        "(1) an exact symbolic certificate for the inverse branch x = (-1/n + sqrt(1/n^2+4t))/2, "
        "showing it really inverts x(x+1/n)=t; "
        "(2) a certified Z3 inequality proving the uniqueness-growth step "
        "d_{n+1} >= d_n whenever both trajectories lie in (1-1/n,1); and "
        "(3) numerical sanity search for the candidate initial value. "
        "A complete machine-checked formalization of the full infinite nested-interval argument "
        "would require a richer proof assistant/library for real analysis than the present kdrag/Z3 setup. "
        "Therefore the overall theorem is not claimed as fully formalized here."
    )
    return {
        "name": "problem_status",
        "passed": False,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    }


def verify() -> Dict[str, Any]:
    checks = [
        _check_kdrag_basic_order_trichotomy(),
        _check_kdrag_monotone_uniqueness_step(),
        _check_sympy_inverse_formula(),
        _check_numerical_sanity(),
        _check_problem_status_explanation(),
    ]
    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))