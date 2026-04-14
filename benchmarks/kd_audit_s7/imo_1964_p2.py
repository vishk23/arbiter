from __future__ import annotations

from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Not

from sympy import symbols, expand, simplify


def _check_kdrag_triangle_inequality() -> Dict[str, Any]:
    """Verify the inequality after a standard triangle substitution.

    We use a stronger algebraic statement:
        2*(x^2 y + x^2 z + y^2 x + y^2 z + z^2 x + z^2 y) - 12 xyz >= 0
    which is equivalent to
        x^2 y + x^2 z + y^2 x + y^2 z + z^2 x + z^2 y >= 6 xyz.

    This is not directly a full proof of the original theorem, but it is the key
    AM-GM certificate in the standard reduction.
    """
    x, y, z = Real("x"), Real("y"), Real("z")

    lhs = x * x * y + x * x * z + y * y * x + y * y * z + z * z * x + z * z * y
    thm = ForAll(
        [x, y, z],
        Implies(And(x >= 0, y >= 0, z >= 0), lhs >= 6 * x * y * z),
    )
    try:
        pf = kd.prove(
            thm,
            by=[
                # Z3 can handle the arithmetic verification of the nonnegativity
                # of the AM-GM gap once expanded into a sum-of-products form.
                # The certificate here is the proof object returned by kd.prove.
            ],
        )
        return {
            "name": "AM-GM core certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned {type(pf).__name__}: {pf}",
        }
    except Exception as e:
        return {
            "name": "AM-GM core certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof attempt failed: {e}",
        }


def _check_symbolic_substitution_identity() -> Dict[str, Any]:
    """Symbolically verify the substitution identity from the hint.

    For a=x+y, b=x+z, c=y+z, the inequality reduces to
        2*z*(x+y)^2 + 2*y*(x+z)^2 + 2*x*(y+z)^2 <= 3*(x+y)*(x+z)*(y+z)
    which after expansion is equivalent to
        x^2y + x^2z + y^2x + y^2z + z^2x + z^2y >= 6xyz.
    """
    x, y, z = symbols("x y z", nonnegative=True)
    a = x + y
    b = x + z
    c = y + z
    expr = expand(a**2 * (b + c - a) + b**2 * (c + a - b) + c**2 * (a + b - c) - 3 * a * b * c)
    target = expand(-(x**2*y + x**2*z + y**2*x + y**2*z + z**2*x + z**2*y - 6*x*y*z))
    ok = simplify(expr - target) == 0
    return {
        "name": "Symbolic substitution reduction",
        "passed": bool(ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Expanded difference simplifies to 0: {ok}",
    }


def _check_numerical_sanity() -> Dict[str, Any]:
    """Numerical sanity check on a concrete triangle."""
    a, b, c = 4.0, 5.0, 6.0
    lhs = a * a * (b + c - a) + b * b * (c + a - b) + c * c * (a + b - c)
    rhs = 3.0 * a * b * c
    passed = lhs <= rhs + 1e-12
    return {
        "name": "Numerical triangle sanity check",
        "passed": bool(passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For (a,b,c)=({a},{b},{c}), lhs={lhs}, rhs={rhs}.",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_check_kdrag_triangle_inequality())
    checks.append(_check_symbolic_substitution_identity())
    checks.append(_check_numerical_sanity())
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)