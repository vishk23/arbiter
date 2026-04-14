from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, expand, simplify


def verify() -> dict:
    checks: List[dict] = []

    # Verified proof using kdrag: prove the simplification for all x.
    x = Real("x")
    expr = (3 * x - 2) * (4 * x + 1) - (3 * x - 2) * 4 * x + 1
    target = 3 * x - 1
    try:
        proof = kd.prove(ForAll([x], expr == target))
        checks.append(
            {
                "name": "symbolic_simplification",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved universally that {(3*x - 2)*(4*x + 1) - (3*x - 2)*4*x + 1} == 3*x - 1.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "symbolic_simplification",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # Numerical sanity check at x = 4.
    x_val = 4
    numeric_value = (3 * x_val - 2) * (4 * x_val + 1) - (3 * x_val - 2) * 4 * x_val + 1
    checks.append(
        {
            "name": "numerical_evaluation_at_4",
            "passed": numeric_value == 11,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct evaluation at x=4 gives {numeric_value}, expected 11.",
        }
    )

    # SymPy symbolic expansion cross-check.
    xs = Symbol("xs")
    sym_expr = (3 * xs - 2) * (4 * xs + 1) - (3 * xs - 2) * 4 * xs + 1
    simplified = simplify(expand(sym_expr))
    checks.append(
        {
            "name": "sympy_expansion_crosscheck",
            "passed": simplified == 3 * xs - 1,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy simplifies the expression to {simplified}.",
        }
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)