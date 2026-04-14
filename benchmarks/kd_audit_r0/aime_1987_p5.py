from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Ints, ForAll, Implies, And

from sympy import Symbol, minimal_polynomial, Integer, factorint


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Verified proof: the key algebraic implication is Z3-encodable.
    # If integers x,y satisfy the equation, then the target value is 588.
    x, y = Ints("x y")
    theorem = ForAll(
        [x, y],
        Implies(
            y * y + 3 * x * x * y * y == 30 * x * x + 517,
            3 * x * x * y * y == 588,
        ),
    )
    try:
        prf = kd.prove(theorem)
        checks.append(
            {
                "name": "z3_proof_target_value",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove() succeeded with proof object: {prf}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "z3_proof_target_value",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove() failed: {type(e).__name__}: {e}",
            }
        )

    # SymPy symbolic sanity: the factorization used in the classical solution.
    # (3x^2 + 1)(y^2 - 10) = 507 follows by rearrangement.
    try:
        # We verify the number-theoretic structure of 507 as in the hint.
        fac = factorint(Integer(507))
        ok_fac = fac == {3: 1, 13: 2}
        checks.append(
            {
                "name": "sympy_factorization_507",
                "passed": ok_fac,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"factorint(507) = {fac}; expected {{3: 1, 13: 2}}.",
            }
        )
        if not ok_fac:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_factorization_507",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy factorization failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the claimed solution x=2, y=7.
    try:
        xv, yv = 2, 7
        lhs = yv * yv + 3 * xv * xv * yv * yv
        rhs = 30 * xv * xv + 517
        target = 3 * xv * xv * yv * yv
        ok_num = (lhs == rhs) and (target == 588)
        checks.append(
            {
                "name": "numerical_check_x2_y7",
                "passed": ok_num,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At x=2, y=7: lhs={lhs}, rhs={rhs}, target={target}.",
            }
        )
        if not ok_num:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_check_x2_y7",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)