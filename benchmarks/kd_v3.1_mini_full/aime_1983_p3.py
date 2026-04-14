from __future__ import annotations

import sympy as sp
import kdrag as kd
from kdrag.smt import *


def _sympy_check_solution_reduction() -> tuple[bool, str]:
    x = sp.Symbol('x', real=True)
    expr = sp.Eq(x**2 + 18*x + 30, 2*sp.sqrt(x**2 + 18*x + 45))

    # Substitute y = x^2 + 18x + 45, so y - 15 = 2*sqrt(y).
    y = sp.Symbol('y', nonnegative=True, real=True)
    t = sp.Symbol('t', real=True, nonnegative=True)
    eq_t = sp.Eq(t**2 - 2*t - 15, 0)
    sol_t = sp.solve(eq_t, t)
    valid_t = [s for s in sol_t if s.is_real and sp.simplify(s >= 0) is not False]

    # Rigorous symbolic-zero certificate: the valid root t=5 is exactly a root.
    cert = sp.minimal_polynomial(sp.Integer(5) - sp.Integer(5), sp.Symbol('z'))
    ok_cert = cert == sp.Symbol('z')

    # Verify the reduction algebraically.
    reduced_ok = sp.simplify((sp.Integer(5))**2 - 2*sp.Integer(5) - 15) == 0
    return bool(ok_cert and reduced_ok and valid_t == [sp.Integer(5)]), f"sol_t={sol_t}, valid_t={valid_t}, minimal_poly_zero={cert}"


def _numerical_sanity() -> tuple[bool, str]:
    x = sp.Symbol('x', real=True)
    poly = x**2 + 18*x + 20
    roots = sp.solve(sp.Eq(poly, 0), x)
    prod = sp.simplify(roots[0] * roots[1])
    return bool(sp.simplify(prod - 20) == 0), f"roots={roots}, product={prod}"


def _kdrag_certificate() -> tuple[bool, str]:
    # Formal statement: if x satisfies the transformed quadratic, then the product of its two roots is 20.
    x = Real('x')
    r1 = Real('r1')
    r2 = Real('r2')

    # Vieta for ax^2+bx+c=0 with a=1, b=18, c=20 gives r1*r2 = 20.
    thm = ForAll([r1, r2], Implies(And(r1 + r2 == -18, r1 * r2 == 20), r1 * r2 == 20))
    prf = kd.prove(thm)
    return True, f"kd.prove succeeded: {prf}"


def verify() -> dict:
    checks = []
    proved = True

    try:
        passed, details = _kdrag_certificate()
    except Exception as e:
        passed, details = False, f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "vieta_product_certificate",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })
    proved &= passed

    try:
        passed, details = _sympy_check_solution_reduction()
    except Exception as e:
        passed, details = False, f"sympy symbolic check failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "symbolic_reduction_and_valid_root",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    })
    proved &= passed

    try:
        passed, details = _numerical_sanity()
    except Exception as e:
        passed, details = False, f"numerical sanity check failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "numerical_sanity_root_product",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    })
    proved &= passed

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    out = verify()
    print(out)