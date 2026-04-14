from typing import Dict, Any

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


TARGET = 912673
EXPECTED_SUM = 16
EXPECTED_ROOT = 97


def _check_kdrag_exact_cube_root() -> Dict[str, Any]:
    if kd is None:
        return {
            "name": "kdrag_exact_cube_root",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment; cannot construct a certified proof.",
        }
    try:
        proof = kd.prove(IntVal(EXPECTED_ROOT) * IntVal(EXPECTED_ROOT) * IntVal(EXPECTED_ROOT) == IntVal(TARGET))
        return {
            "name": "kdrag_exact_cube_root",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified proof object obtained: {proof}. This proves {EXPECTED_ROOT}^3 = {TARGET}.",
        }
    except Exception as e:
        return {
            "name": "kdrag_exact_cube_root",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_kdrag_sum_from_digits() -> Dict[str, Any]:
    if kd is None:
        return {
            "name": "kdrag_digit_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag is unavailable in this environment; cannot certify digit sum.",
        }
    try:
        A = IntVal(9)
        B = IntVal(7)
        proof = kd.prove(A + B == IntVal(EXPECTED_SUM))
        return {
            "name": "kdrag_digit_sum",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified proof object obtained: {proof}. Hence A+B = 9+7 = {EXPECTED_SUM}.",
        }
    except Exception as e:
        return {
            "name": "kdrag_digit_sum",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_sympy_exact_integer_root() -> Dict[str, Any]:
    n, exact = sp.integer_nthroot(TARGET, 3)
    passed = bool(exact and n == EXPECTED_ROOT and n**3 == TARGET)
    details = f"integer_nthroot({TARGET}, 3) -> (n={n}, exact={exact}); n^3={n**3}."
    return {
        "name": "sympy_exact_integer_root",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": details,
    }


def _check_numerical_sanity() -> Dict[str, Any]:
    val = (EXPECTED_ROOT ** 3)
    passed = (val == TARGET)
    details = f"Concrete sanity check: {EXPECTED_ROOT}^3 = {val}, target = {TARGET}."
    return {
        "name": "numerical_sanity",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    }


def verify() -> Dict[str, Any]:
    checks = [
        _check_kdrag_exact_cube_root(),
        _check_kdrag_sum_from_digits(),
        _check_sympy_exact_integer_root(),
        _check_numerical_sanity(),
    ]
    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import pprint
    pprint.pprint(verify())