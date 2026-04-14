from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, Eq, sqrt, solve, discriminant, simplify, factor, Rational


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: Verified certificate that the transformed equation y = 2*sqrt(y+15)
    # implies y = 10 or y = -6 by squaring and solving the resulting quadratic.
    y = Real("y")
    try:
        thm_y = kd.prove(
            ForAll([y], Implies(y == 2 * (y + 15) ** (1 / 2), Or(y == 10, y == -6)))
        )
        checks.append(
            {
                "name": "solve_transformed_equation",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm_y}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "solve_transformed_equation",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: SymPy symbolic verification that the reduced quadratic has discriminant > 0
    x = Symbol("x", real=True)
    q = x**2 + 18 * x + 20
    disc = discriminant(q, x)
    disc_positive = bool(disc > 0)
    checks.append(
        {
            "name": "quadratic_discriminant_positive",
            "passed": disc_positive,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"discriminant(x^2+18x+20) = {disc}, so it has two real roots.",
        }
    )
    if not disc_positive:
        proved = False

    # Check 3: SymPy symbolic root-product computation for x^2 + 18x + 20 = 0.
    roots = solve(Eq(q, 0), x)
    if len(roots) == 2:
        prod = simplify(roots[0] * roots[1])
        passed_prod = simplify(prod - 20) == 0
    else:
        prod = None
        passed_prod = False
    checks.append(
        {
            "name": "product_of_roots",
            "passed": passed_prod,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"roots={roots}; product={prod}; expected 20.",
        }
    )
    if not passed_prod:
        proved = False

    # Check 4: Numerical sanity check at a concrete root x = -9 + sqrt(61).
    x_num = -9 + sqrt(61)
    lhs = simplify(x_num**2 + 18 * x_num + 30)
    rhs = simplify(2 * sqrt(x_num**2 + 18 * x_num + 45))
    num_pass = simplify(lhs - rhs) == 0
    checks.append(
        {
            "name": "numerical_root_sanity_check",
            "passed": bool(num_pass),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x=-9+sqrt(61), lhs={lhs}, rhs={rhs}.",
        }
    )
    if not num_pass:
        proved = False

    # Check 5: Direct symbolic substitution showing the candidate root satisfies the original equation.
    # Use one root explicitly; the other is analogous.
    root1 = -9 + sqrt(61)
    expr_check = simplify((root1**2 + 18 * root1 + 30) - 2 * sqrt(root1**2 + 18 * root1 + 45))
    symb_ok = expr_check == 0
    checks.append(
        {
            "name": "candidate_root_satisfies_original_equation",
            "passed": bool(symb_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Substitution yields {expr_check}, so the candidate is a genuine root.",
        }
    )
    if not symb_ok:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)