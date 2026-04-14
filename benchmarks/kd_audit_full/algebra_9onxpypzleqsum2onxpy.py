from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, Rational, simplify


def verify() -> dict:
    checks: List[dict] = []
    proved_all = True

    # Check 1: verified kdrag proof of the core inequality after clearing denominators.
    # For positive a,b,c, 9/(a+b+c) <= 2/(a+b)+2/(b+c)+2/(c+a)
    # is equivalent to 9*(1) <= 2*(a+b+c)/(a+b) + ... after multiplying by positive (a+b)(b+c)(c+a).
    # The polynomial form below is exactly what Z3 can prove.
    x, y, z = Reals("x y z")
    lhs = 9 * (x + y) * (y + z) * (z + x)
    rhs = 2 * (x + y + z) * ((y + z) * (z + x) + (x + y) * (z + x) + (x + y) * (y + z))
    theorem = ForAll(
        [x, y, z],
        Implies(
            And(x > 0, y > 0, z > 0),
            lhs <= rhs,
        ),
    )
    try:
        prf = kd.prove(theorem)
        checks.append(
            {
                "name": "cleared_denominator_inequality",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {prf}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "cleared_denominator_inequality",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: symbolic simplification of the standard midpoint-style numerical sanity point.
    # At x=y=z=1, the inequality becomes 3 <= 3.
    try:
        sx = Rational(1)
        sy = Rational(1)
        sz = Rational(1)
        expr = simplify(Rational(9, sx + sy + sz) - (Rational(2, sx + sy) + Rational(2, sy + sz) + Rational(2, sz + sx)))
        passed = (expr <= 0)
        checks.append(
            {
                "name": "numerical_sanity_at_1_1_1",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Difference at x=y=z=1 simplifies to {expr}.",
            }
        )
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_at_1_1_1",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)