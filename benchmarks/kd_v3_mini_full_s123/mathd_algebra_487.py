from __future__ import annotations

from math import sqrt as _py_sqrt

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def _sympy_distance_certificate():
    x = sp.Symbol('x')
    sol = sp.solve(sp.Eq(x**2 + x - 1, 0), x)
    if len(sol) != 2:
        return False, f"Expected 2 solutions, got {len(sol)}"
    x1, x2 = sol
    y1, y2 = x1**2, x2**2
    dist = sp.simplify(sp.sqrt((x1 - x2)**2 + (y1 - y2)**2))
    return sp.simplify(dist - sp.sqrt(10)) == 0, f"Computed distance simplifies to {dist}"


def _kdrag_distance_certificate():
    if kd is None:
        return False, "kdrag is unavailable"

    # Let the two intersection x-coordinates be the roots of x^2 + x - 1 = 0.
    x1, x2 = Reals('x1 x2')
    s, p = Reals('s p')
    # Encode Vieta-like relations for the roots.
    # If x1,x2 are roots, then x1+x2=-1 and x1*x2=-1.
    thm = kd.prove(
        ForAll([x1, x2],
            Implies(
                And(x1 + x2 == -1, x1 * x2 == -1),
                (x1 - x2) * (x1 - x2) + (x1 * x1 - x2 * x2) * (x1 * x1 - x2 * x2) == 10
            )
        )
    )
    return True, str(thm)


def verify() -> dict:
    checks = []

    sympy_passed, sympy_details = _sympy_distance_certificate()
    checks.append({
        "name": "sympy_symbolic_distance",
        "passed": bool(sympy_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": sympy_details,
    })

    # Numerical sanity check at the explicitly stated intersection points.
    x1 = (-1 + _py_sqrt(5)) / 2
    x2 = (-1 - _py_sqrt(5)) / 2
    y1 = x1 * x1
    y2 = x2 * x2
    dist_num = _py_sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
    num_passed = abs(dist_num - _py_sqrt(10)) < 1e-12
    checks.append({
        "name": "numerical_distance_sanity",
        "passed": bool(num_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"distance={dist_num}, expected={_py_sqrt(10)}",
    })

    # kdrag proof certificate: prove the algebraic identity for two roots satisfying
    # the Vieta relations. This is a certified Z3 proof if kdrag is available.
    if kd is not None:
        try:
            x1r, x2r = Reals('x1r x2r')
            proof = kd.prove(
                ForAll([x1r, x2r],
                    Implies(
                        And(x1r + x2r == -1, x1r * x2r == -1),
                        (x1r - x2r) * (x1r - x2r) + (x1r * x1r - x2r * x2r) * (x1r * x1r - x2r * x2r) == 10
                    )
                )
            )
            checks.append({
                "name": "kdrag_vieta_distance_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(proof),
            })
        except Exception as e:
            checks.append({
                "name": "kdrag_vieta_distance_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            })
    else:
        checks.append({
            "name": "kdrag_vieta_distance_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag unavailable in runtime",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)