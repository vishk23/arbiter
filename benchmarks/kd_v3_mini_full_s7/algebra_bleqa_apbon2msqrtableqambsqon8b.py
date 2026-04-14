from __future__ import annotations

import math
from typing import Any, Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Real, ForAll, Implies, And, Not
except Exception:  # pragma: no cover
    kd = None


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # ---------------------------------------------------------------------
    # Check 1: Symbolic identity / factorization used in the proof.
    # For x = sqrt(t),
    #   (x^2 - 1)^2 - 4(x - 1)^2 = (x - 1)^3 (x + 3)
    # which is nonnegative for x >= 1.
    # ---------------------------------------------------------------------
    x = sp.symbols("x", positive=True)
    expr = (x**2 - 1) ** 2 - 4 * (x - 1) ** 2
    factored = sp.factor(expr)
    sympy_ok = sp.simplify(factored - (x - 1) ** 3 * (x + 3)) == 0
    checks.append(
        {
            "name": "sympy_factorization",
            "passed": bool(sympy_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"factor((x**2 - 1)**2 - 4*(x - 1)**2) = {factored}",
        }
    )
    proved = proved and bool(sympy_ok)

    # ---------------------------------------------------------------------
    # Check 2: Verified proof with kdrag for a transformed inequality.
    # Let x >= 1. Since (x-1)^2 >= 0 and x+3 >= 0, we have
    #   (x^2 - 1)^2 - 4(x - 1)^2 = (x - 1)^3(x + 3) >= 0,
    # hence 4(x - 1)^2 <= (x^2 - 1)^2.
    # This is a Z3-encodable polynomial inequality over reals.
    # ---------------------------------------------------------------------
    if kd is None:
        checks.append(
            {
                "name": "kdrag_transformed_inequality",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kdrag is unavailable in this environment.",
            }
        )
        proved = False
    else:
        xr = Real("x")
        try:
            proof = kd.prove(
                ForAll([xr], Implies(xr >= 1, (xr**2 - 1) ** 2 >= 4 * (xr - 1) ** 2))
            )
            checks.append(
                {
                    "name": "kdrag_transformed_inequality",
                    "passed": True,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"Proof object obtained: {proof}",
                }
            )
        except Exception as e:  # pragma: no cover
            checks.append(
                {
                    "name": "kdrag_transformed_inequality",
                    "passed": False,
                    "backend": "kdrag",
                    "proof_type": "certificate",
                    "details": f"kdrag proof failed: {type(e).__name__}: {e}",
                }
            )
            proved = False

    # ---------------------------------------------------------------------
    # Check 3: Numerical sanity check with concrete values.
    # Choose a = 9, b = 4 with b <= a.
    # LHS = (a+b)/2 - sqrt(ab), RHS = (a-b)^2/(8b).
    # ---------------------------------------------------------------------
    a_val = 9.0
    b_val = 4.0
    lhs = (a_val + b_val) / 2.0 - math.sqrt(a_val * b_val)
    rhs = (a_val - b_val) ** 2 / (8.0 * b_val)
    num_ok = lhs <= rhs + 1e-12
    checks.append(
        {
            "name": "numerical_sanity",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"a={a_val}, b={b_val}, lhs={lhs:.12g}, rhs={rhs:.12g}",
        }
    )
    proved = proved and bool(num_ok)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)