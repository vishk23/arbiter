from __future__ import annotations

from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Or, Not

from sympy import symbols, simplify, expand


def _numerical_sanity() -> Dict[str, Any]:
    # One concrete triangle: a=3, b=4, c=5.
    a, b, c = 3.0, 4.0, 5.0
    lhs = a * a * (b + c - a) + b * b * (c + a - b) + c * c * (a + b - c)
    rhs = 3 * a * b * c
    passed = lhs <= rhs + 1e-12
    return {
        "name": "numerical_sanity_example_triangle",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For (a,b,c)=({a},{b},{c}), lhs={lhs}, rhs={rhs}.",
    }


def _kdrag_proof() -> Dict[str, Any]:
    # Prove the equivalent inequality after substituting a=x+y, b=x+z, c=y+z:
    # 2z(x+y)^2 + 2y(x+z)^2 + 2x(y+z)^2 <= 3(x+y)(x+z)(y+z)
    # For x,y,z >= 0 this is equivalent to
    # x^2y + x^2z + y^2x + y^2z + z^2x + z^2y >= 6xyz,
    # which follows from AM-GM.
    x = Real("x")
    y = Real("y")
    z = Real("z")

    am_gm_form = ForAll(
        [x, y, z],
        Implies(
            And(x >= 0, y >= 0, z >= 0),
            x * x * y + x * x * z + y * y * x + y * y * z + z * z * x + z * z * y >= 6 * x * y * z,
        ),
    )

    try:
        prf = kd.prove(am_gm_form)
        return {
            "name": "am_gm_core_inequality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned {type(prf).__name__}: {prf}",
        }
    except Exception as e:
        return {
            "name": "am_gm_core_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof attempt failed: {type(e).__name__}: {e}",
        }


def _symbolic_equivalence_check() -> Dict[str, Any]:
    # Verify the algebraic rearrangement from the substitution a=x+y, b=x+z, c=y+z.
    x, y, z = symbols("x y z", real=True)
    a = x + y
    b = x + z
    c = y + z

    lhs = a**2 * (b + c - a) + b**2 * (c + a - b) + c**2 * (a + b - c)
    rhs = 3 * a * b * c

    transformed = simplify(expand(rhs - lhs) - (x**2 * y + x**2 * z + y**2 * x + y**2 * z + z**2 * x + z**2 * y - 6 * x * y * z))
    passed = transformed == 0
    return {
        "name": "symbolic_substitution_equivalence",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"After substitution a=x+y, b=x+z, c=y+z, symbolic remainder simplifies to {transformed}.",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_kdrag_proof())
    checks.append(_symbolic_equivalence_check())
    checks.append(_numerical_sanity())

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)