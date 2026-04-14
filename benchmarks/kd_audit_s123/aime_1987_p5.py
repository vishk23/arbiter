from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Ints, ForAll, Implies, And

from sympy import Symbol, minimal_polynomial, factorint


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: Verified theorem in kdrag/Z3.
    try:
        x, y = Ints('x y')
        # Derived identity from the problem statement:
        # y^2 + 3x^2 y^2 = 30x^2 + 517
        # => (3x^2 + 1)(y^2 - 10) = 507
        # and the only integer solution gives 3x^2 y^2 = 588.
        thm = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(y * y + 3 * x * x * y * y == 30 * x * x + 517),
                    3 * x * x * y * y == 588,
                ),
            )
        )
        checks.append(
            {
                "name": "main_diophantine_result",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "main_diophantine_result",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Symbolic factorization / arithmetic consistency check.
    try:
        # 517 - 10 = 507 = 3 * 13^2
        n = 517 - 10
        fac = factorint(n)
        ok = (n == 507 and fac == {3: 1, 13: 2})
        checks.append(
            {
                "name": "factorization_507",
                "passed": ok,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"507 factorization is {fac}; expected {{3: 1, 13: 2}}.",
            }
        )
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "factorization_507",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"factorization check failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Numerical sanity check at the claimed solution x=2, y=7.
    try:
        xv, yv = 2, 7
        lhs = yv * yv + 3 * xv * xv * yv * yv
        rhs = 30 * xv * xv + 517
        target = 3 * xv * xv * yv * yv
        ok = (lhs == rhs == 567) and (target == 588)
        checks.append(
            {
                "name": "numerical_sanity_at_solution",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At x=2, y=7: lhs={lhs}, rhs={rhs}, 3x^2y^2={target}.",
            }
        )
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_at_solution",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import pprint
    pprint.pprint(verify())