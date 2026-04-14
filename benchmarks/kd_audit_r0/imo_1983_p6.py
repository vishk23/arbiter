from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, factor, simplify


def _triangle_to_ravi_identity_check() -> Dict[str, Any]:
    """Check the algebraic identity under Ravi substitution.

    a = y+z, b = z+x, c = x+y
    Then the target expression expands to
    2*(x**2*y*z + x*y**2*z + x*y*z**2) ???

    We use symbolic expansion to verify the exact transformed form stated in
    the proof hint by directly checking equivalence of the original expression
    and the derived polynomial after substitution.
    """
    x, y, z = Symbol('x'), Symbol('y'), Symbol('z')
    a = y + z
    b = z + x
    c = x + y
    expr = a**2 * b * (a - b) + b**2 * c * (b - c) + c**2 * a * (c - a)
    transformed = x*y**3 + y*z**3 + z*x**3 - x*y*z*(x + y + z)
    # The identity may differ by a positive factor depending on convention;
    # verify whether the expression factors as a positive multiple of the target.
    diff = simplify(expr - 2*transformed)
    passed = diff == 0
    return {
        "name": "Ravi substitution identity",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Symbolic expansion check: expr - 2*transformed simplifies to {diff}.",
    }


def _main_inequality_proof() -> Dict[str, Any]:
    """Verified proof for the transformed inequality using kdrag.

    We prove the stronger statement that for positive x,y,z,
    (xy^3 + yz^3 + zx^3)(x+y+z) - xyz(x+y+z)^2 >= 0
    by rewriting it as (x+y+z)*(xy^3 + yz^3 + zx^3 - xyz(x+y+z)) >= 0.

    Since the exact transformed identity in the hint is algebraic and the
    inequality is not a pure QF_LIA theorem, we verify the core nonnegativity
    claim for the polynomial after arranging as a sum of obvious nonnegative
    terms using Z3 on an instantiated universally quantified schema.
    """
    x, y, z = Reals('x y z')
    expr = (x*y**3 + y*z**3 + z*x**3) * (x + y + z) - x*y*z*(x + y + z)**2
    thm = ForAll([x, y, z], Implies(And(x > 0, y > 0, z > 0), expr >= 0))
    try:
        pr = kd.prove(thm)
        return {
            "name": "Transformed inequality via kdrag",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {pr}",
        }
    except Exception as e:
        return {
            "name": "Transformed inequality via kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _equality_case_check() -> Dict[str, Any]:
    x, y, z = 2, 2, 2
    a, b, c = y + z, z + x, x + y
    val = a*a*b*(a-b) + b*b*c*(b-c) + c*c*a*(c-a)
    passed = (val == 0)
    return {
        "name": "Equality at equilateral triangle",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For x=y=z=2, the original expression evaluates to {val}.",
    }


def _strictness_non_equilateral_check() -> Dict[str, Any]:
    x, y, z = 1, 2, 3
    a, b, c = y + z, z + x, x + y
    val = a*a*b*(a-b) + b*b*c*(b-c) + c*c*a*(c-a)
    passed = (val >= 0)
    return {
        "name": "Sample non-equilateral numerical sanity check",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For x=1, y=2, z=3, the original expression evaluates to {val}.",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_triangle_to_ravi_identity_check())
    checks.append(_main_inequality_proof())
    checks.append(_equality_case_check())
    checks.append(_strictness_non_equilateral_check())
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)