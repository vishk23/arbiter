from __future__ import annotations

from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import *
from sympy import Rational, Symbol, nsimplify


def _check_kdrag_tan_from_sec_plus_tan() -> Dict[str, Any]:
    t = Real("t")
    s = RealVal("22/7")
    target = RealVal("435/308")
    thm = ForAll(
        [t],
        Implies((s - t) * (s + t) == 1, t == target),
    )
    try:
        pf = kd.prove(thm)
        return {
            "name": "kdrag_tan_value_from_sec_plus_tan",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        }
    except kd.kernel.LemmaError as e:
        return {
            "name": "kdrag_tan_value_from_sec_plus_tan",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove from reciprocal identity (sec-tan)(sec+tan)=1: {e}",
        }


def _check_kdrag_csc_plus_cot_from_tan() -> Dict[str, Any]:
    y = Real("y")
    t = RealVal("435/308")
    target = RealVal("29/841")
    thm = ForAll(
        [y],
        Implies(y == (1 - t) / (1 + t), y == target),
    )
    try:
        pf = kd.prove(thm)
        return {
            "name": "kdrag_csc_plus_cot_value",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        }
    except kd.kernel.LemmaError as e:
        return {
            "name": "kdrag_csc_plus_cot_value",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove y=(1-t)/(1+t)=29/841: {e}",
        }


def _check_kdrag_final_sum() -> Dict[str, Any]:
    m = Int("m")
    n = Int("n")
    thm = ForAll(
        [m, n],
        Implies(And(m == 29, n == 841), m + n == 870),
    )
    try:
        pf = kd.prove(thm)
        return {
            "name": "kdrag_final_sum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(pf),
        }
    except kd.kernel.LemmaError as e:
        return {
            "name": "kdrag_final_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 29+841=870: {e}",
        }


def _check_sympy_exact_sanity() -> Dict[str, Any]:
    try:
        s = Rational(22, 7)
        t = (s**2 - 1) / (2 * s)
        y = (1 - t) / (1 + t)
        passed = (t == Rational(435, 308)) and (y == Rational(29, 841))
        return {
            "name": "sympy_exact_rational_sanity",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exact rational computation gives tan=x? t={t}, csc+cot={y}",
        }
    except Exception as e:
        return {
            "name": "sympy_exact_rational_sanity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy exact computation failed: {e}",
        }


def _check_numerical_sanity() -> Dict[str, Any]:
    try:
        s = Rational(22, 7)
        t = Rational(435, 308)
        y = Rational(29, 841)
        lhs1 = nsimplify((1 + t * t) ** Rational(1, 2) + t)
        lhs2 = nsimplify((1 - t) / (1 + t))
        passed = abs(float(lhs1) - float(s)) < 1e-12 and abs(float(lhs2) - float(y)) < 1e-12
        return {
            "name": "numerical_sanity",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"sqrt(1+t^2)+t ≈ {float(lhs1):.12f}, target 22/7 ≈ {float(s):.12f}; (1-t)/(1+t) ≈ {float(lhs2):.12f}",
        }
    except Exception as e:
        return {
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}",
        }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_check_kdrag_tan_from_sec_plus_tan())
    checks.append(_check_kdrag_csc_plus_cot_from_tan())
    checks.append(_check_kdrag_final_sum())
    checks.append(_check_sympy_exact_sanity())
    checks.append(_check_numerical_sanity())

    proved = all(ch.get("passed", False) for ch in checks)
    return {
        "proved": proved,
        "checks": checks,
        "answer": 870,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2, sort_keys=True))