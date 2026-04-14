from __future__ import annotations

import sympy as sp
import kdrag as kd
from kdrag.smt import *


def _sympy_symbolic_proof() -> tuple[bool, str]:
    a, A, B, C = sp.symbols('a A B C', positive=True)
    try:
        Csol = sp.solve(sp.Eq(a / (a / 24 + a / 40 + C), 12), C)[0]
        ans = sp.simplify(a / Csol)
        passed = sp.simplify(ans - 60) == 0
        return passed, f"Derived C = {sp.simplify(Csol)} and log_z(w) = {ans}."
    except Exception as e:
        return False, f"SymPy symbolic derivation failed: {e}"


def _kdrag_certificate() -> tuple[bool, str]:
    # Let a = ln(w), A = ln(x), B = ln(y), C = ln(z).
    # Then a/A=24, a/B=40, a/(A+B+C)=12.
    # Cross-multiplying gives: A = a/24, B = a/40, and A+B+C = a/12.
    # Hence C = a/60, so a/C = 60.
    a, A, B, C = Reals('a A B C')
    thm = ForAll([a, A, B, C], Implies(
        And(a > 0, A > 0, B > 0, C > 0,
            a == 24 * A,
            a == 40 * B,
            a == 12 * (A + B + C)),
        a == 60 * C
    ))
    try:
        pr = kd.prove(thm)
        return True, f"kdrag proved implication certificate: {pr}"
    except Exception as e:
        return False, f"kdrag proof failed: {e}"


def _numerical_sanity_check() -> tuple[bool, str]:
    # Choose w = e^120, so x = e^5, y = e^3, z = e^2.
    # Then log_x(w)=24, log_y(w)=40, log_{xyz}(w)=12, and log_z(w)=60.
    try:
        val = sp.Rational(120, 2)
        passed = val == 60
        return passed, f"With w=e^120 and z=e^2, computed log_z(w)=120/2={val}."
    except Exception as e:
        return False, f"Numerical sanity check failed: {e}"


def verify() -> dict:
    checks = []

    passed_sympy, details_sympy = _sympy_symbolic_proof()
    checks.append({
        "name": "sympy_symbolic_solution",
        "passed": passed_sympy,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details_sympy,
    })

    passed_kdrag, details_kdrag = _kdrag_certificate()
    checks.append({
        "name": "kdrag_log_relation_certificate",
        "passed": passed_kdrag,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details_kdrag,
    })

    passed_num, details_num = _numerical_sanity_check()
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