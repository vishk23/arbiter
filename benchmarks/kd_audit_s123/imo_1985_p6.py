from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, Rational, minimal_polynomial


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: verified kdrag proof that if 0 < x < 1 then x < x(x+1/n) is not universally true;
    # instead we prove a useful algebraic fact used in the uniqueness argument:
    # if 0 <= x <= y and x + y + 1/n >= 1, then y - x does not decrease under the recurrence.
    # We encode a concrete monotonicity lemma that is directly Z3-encodable.
    x, y, n = Reals("x y n")
    try:
        thm = kd.prove(
            ForAll(
                [x, y, n],
                Implies(
                    And(n > 0, y >= x, x >= 0, x <= 1, y <= 1),
                    (y * (y + 1 / n) - x * (x + 1 / n)) >= (y - x),
                ),
            )
        )
        checks.append(
            {
                "name": "recurrence_difference_monotonicity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned {type(thm).__name__}.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "recurrence_difference_monotonicity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: symbolic algebraic-zero certificate for a simple exact identity used as a sanity check.
    # This is rigorous via minimal_polynomial; here the expression is exactly zero.
    try:
        z = Symbol("z")
        expr = Rational(0)
        mp = minimal_polynomial(expr, z)
        ok = (mp == z)
        checks.append(
            {
                "name": "symbolic_zero_certificate",
                "passed": bool(ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"minimal_polynomial(0, z) = {mp}.",
            }
        )
        proved = proved and bool(ok)
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "symbolic_zero_certificate",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic check failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: numerical sanity check for the recurrence at a concrete x1.
    # We test a known admissible-ish value numerically for the first few terms.
    try:
        x1 = 0.5
        vals = [x1]
        ok = True
        details_parts = []
        for k in range(1, 8):
            xn = vals[-1]
            xnext = xn * (xn + 1.0 / k)
            details_parts.append(f"n={k}: x_n={xn:.12g}, x_(n+1)={xnext:.12g}")
            if not (0 < xn < xnext < 1):
                ok = False
                break
            vals.append(xnext)
        checks.append(
            {
                "name": "numerical_sanity_recurrence_sample",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "; ".join(details_parts),
            }
        )
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_recurrence_sample",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    # This module does not fully formalize the olympiad proof in the provided backend.
    # We therefore report proved=False unless every check above passed, but note that the
    # main theorem itself is not mechanically proven here.
    proved = False if not all(c["passed"] for c in checks) else False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2, sort_keys=True))