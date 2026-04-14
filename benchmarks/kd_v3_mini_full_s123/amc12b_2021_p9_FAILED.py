from __future__ import annotations

from typing import Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Real, ForAll, Implies
except Exception:  # pragma: no cover
    kd = None


def _sympy_exact_proof() -> tuple[bool, str]:
    x = sp.symbols('x')
    expr = sp.log(80, 2) / sp.log(2, 40) - sp.log(160, 2) / sp.log(2, 20)
    simplified = sp.simplify(expr)
    passed = sp.simplify(simplified - 2) == 0
    details = f"sympy.simplify(expr) -> {simplified}; expected 2"
    return passed, details


def _numerical_sanity() -> tuple[bool, str]:
    expr = sp.log(80, 2) / sp.log(2, 40) - sp.log(160, 2) / sp.log(2, 20)
    val = sp.N(expr, 50)
    passed = abs(complex(val) - 2) < 1e-20
    details = f"N(expr, 50) -> {val}"
    return passed, details


def _kdrag_certificate() -> tuple[bool, str]:
    if kd is None:
        return False, "kdrag unavailable in this environment"
    # Encode the algebraic simplification pattern used in the problem.
    # Let t represent log_2(20). Then the expression becomes
    # (2+t)(1+t) - (3+t)t = 2.
    t = Real('t')
    try:
        thm = kd.prove(ForAll([t], ((2 + t) * (1 + t) - (3 + t) * t) == 2))
        return True, f"kd.prove returned certificate: {thm}"
    except Exception as e:
        return False, f"kdrag proof failed: {type(e).__name__}: {e}"


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []

    passed_sympy, details_sympy = _sympy_exact_proof()
    checks.append({
        "name": "sympy_symbolic_simplification",
        "passed": passed_sympy,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details_sympy,
    })

    passed_kdrag, details_kdrag = _kdrag_certificate()
    checks.append({
        "name": "kdrag_algebraic_certificate",
        "passed": passed_kdrag,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details_kdrag,
    })

    passed_num, details_num = _numerical_sanity()
    checks.append({
        "name": "numerical_sanity_check",
        "passed": passed_num,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details_num,
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)