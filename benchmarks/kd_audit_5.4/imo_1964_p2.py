from __future__ import annotations

from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, simplify


def _check_algebraic_substitution_identity() -> Dict[str, Any]:
    x, y, z = symbols('x y z', real=True)
    a = x + y
    b = x + z
    c = y + z
    lhs_original = a**2 * (b + c - a) + b**2 * (c + a - b) + c**2 * (a + b - c)
    rhs_original = 3 * a * b * c
    expr = expand(rhs_original - lhs_original)
    target = expand((x + y) * (x + z) * (y + z) * 3 - (2 * z * (x + y) ** 2 + 2 * y * (x + z) ** 2 + 2 * x * (y + z) ** 2))
    passed = simplify(expr - target) == 0
    return {
        "name": "substitution_identity_sympy",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "numerical",
        "details": "Verified by exact symbolic expansion that under a=x+y, b=x+z, c=y+z, the original inequality becomes 2z(x+y)^2+2y(x+z)^2+2x(y+z)^2 <= 3(x+y)(x+z)(y+z).",
    }


def _check_amgm_core_kdrag() -> Dict[str, Any]:
    try:
        x, y, z = Reals('x y z')
        thm = ForAll(
            [x, y, z],
            Implies(
                And(x >= 0, y >= 0, z >= 0),
                x * x * y + x * x * z + y * y * x + y * y * z + z * z * x + z * z * y >= 6 * x * y * z,
            ),
        )
        pf = kd.prove(thm)
        return {
            "name": "amgm_core_kdrag",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3-certified proof object obtained: {pf}",
        }
    except Exception as e:
        return {
            "name": "amgm_core_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_triangle_parameterization_kdrag() -> Dict[str, Any]:
    try:
        a, b, c = Reals('a b c')
        x, y, z = Reals('x y z')
        thm = ForAll(
            [a, b, c],
            Implies(
                And(a > 0, b > 0, c > 0, a + b > c, a + c > b, b + c > a),
                Exists(
                    [x, y, z],
                    And(
                        x > 0,
                        y > 0,
                        z > 0,
                        a == x + y,
                        b == x + z,
                        c == y + z,
                    ),
                ),
            ),
        )
        pf = kd.prove(thm)
        return {
            "name": "triangle_parameterization_kdrag",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified existence of x=(a+b-c)/2, y=(a+c-b)/2, z=(b+c-a)/2 > 0 via kdrag: {pf}",
        }
    except Exception as e:
        return {
            "name": "triangle_parameterization_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_main_inequality_kdrag() -> Dict[str, Any]:
    try:
        x, y, z = Reals('x y z')
        thm = ForAll(
            [x, y, z],
            Implies(
                And(x >= 0, y >= 0, z >= 0),
                2 * z * (x + y) * (x + y) + 2 * y * (x + z) * (x + z) + 2 * x * (y + z) * (y + z)
                <= 3 * (x + y) * (x + z) * (y + z),
            ),
        )
        pf = kd.prove(thm)
        return {
            "name": "main_substituted_inequality_kdrag",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified the substituted inequality directly for all x,y,z >= 0: {pf}",
        }
    except Exception as e:
        return {
            "name": "main_substituted_inequality_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_numerical_sanity() -> Dict[str, Any]:
    samples = [
        (3.0, 4.0, 5.0),
        (5.0, 5.0, 6.0),
        (2.5, 3.0, 4.0),
        (7.0, 8.0, 9.0),
    ]
    ok = True
    lines = []
    for a, b, c in samples:
        lhs = a * a * (b + c - a) + b * b * (c + a - b) + c * c * (a + b - c)
        rhs = 3 * a * b * c
        passed = lhs <= rhs + 1e-9
        ok = ok and passed
        lines.append(f"(a,b,c)=({a},{b},{c}): lhs={lhs:.10f}, rhs={rhs:.10f}, passed={passed}")
    return {
        "name": "numerical_sanity_samples",
        "passed": ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": " ; ".join(lines),
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = [
        _check_algebraic_substitution_identity(),
        _check_triangle_parameterization_kdrag(),
        _check_amgm_core_kdrag(),
        _check_main_inequality_kdrag(),
        _check_numerical_sanity(),
    ]
    proved = all(ch["passed"] for ch in checks) and any(
        ch["passed"] and ch["proof_type"] == "certificate" for ch in checks
    )
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, default=str))