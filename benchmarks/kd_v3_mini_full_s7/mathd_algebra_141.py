from __future__ import annotations

from typing import Dict, List, Any

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: Verified proof via kdrag/Z3 for the algebraic derivation
    # Let a, b be the side lengths. From a+b=27 and ab=180, prove a^2+b^2=369.
    if kd is None:
        checks.append({
            "name": "kdrag_diagonal_squared_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag backend unavailable in this environment.",
        })
        proved = False
    else:
        a, b = Ints("a b")
        try:
            thm = kd.prove(
                ForAll(
                    [a, b],
                    Implies(
                        And(a + b == 27, a * b == 180),
                        a * a + b * b == 369,
                    ),
                )
            )
            checks.append({
                "name": "kdrag_diagonal_squared_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified theorem: {thm}",
            })
        except Exception as e:
            checks.append({
                "name": "kdrag_diagonal_squared_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            })
            proved = False

    # Check 2: Symbolic verification using the identity x^2 + y^2 = (x+y)^2 - 2xy
    x, y = sp.symbols("x y")
    expr = (x + y) ** 2 - 2 * x * y
    symbolic_value = sp.expand(expr.subs({x + y: 27, x * y: 180}))
    passed_symbolic = sp.simplify(symbolic_value - 369) == 0
    checks.append({
        "name": "sympy_identity_evaluation",
        "passed": bool(passed_symbolic),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Expanded expression evaluates to {symbolic_value}; expected 369.",
    })
    if not passed_symbolic:
        proved = False

    # Check 3: Numerical sanity check with the concrete side lengths 12 and 15.
    # Area and perimeter match, and diagonal squared is 369.
    a0, b0 = 12, 15
    area_ok = (a0 * b0 == 180)
    peri_ok = (2 * (a0 + b0) == 54)
    diag_sq = a0 * a0 + b0 * b0
    numeric_ok = area_ok and peri_ok and diag_sq == 369
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(numeric_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Using sides 12 and 15: area={a0*b0}, perimeter={2*(a0+b0)}, diagonal^2={diag_sq}.",
    })
    if not numeric_ok:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)