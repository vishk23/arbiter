from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved_all = True

    # Variables
    a11, a12, a13 = Reals("a11 a12 a13")
    a21, a22, a23 = Reals("a21 a22 a23")
    a31, a32, a33 = Reals("a31 a32 a33")
    x1, x2, x3 = Reals("x1 x2 x3")

    # Hypotheses encoding the problem conditions.
    conds = And(
        a11 > 0,
        a22 > 0,
        a33 > 0,
        a12 < 0,
        a13 < 0,
        a21 < 0,
        a23 < 0,
        a31 < 0,
        a32 < 0,
        a11 + a12 + a13 > 0,
        a21 + a22 + a23 > 0,
        a31 + a32 + a33 > 0,
        a11 * x1 + a12 * x2 + a13 * x3 == 0,
        a21 * x1 + a22 * x2 + a23 * x3 == 0,
        a31 * x1 + a32 * x2 + a33 * x3 == 0,
    )

    # Main theorem: the only solution is the zero vector.
    thm = ForAll(
        [a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3],
        Implies(
            conds,
            And(x1 == 0, x2 == 0, x3 == 0),
        ),
    )

    try:
        proof = kd.prove(thm)
        checks.append(
            {
                "name": "main_uniqueness_theorem",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded and returned a Proof object: {proof}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "main_uniqueness_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed to discharge the quantified theorem automatically: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: choose concrete coefficients satisfying the hypotheses,
    # then verify that the concrete system has only the zero solution by direct computation.
    # Example matrix with positive diagonal, negative off-diagonals, and positive row sums.
    A = [
        [3.0, -1.0, -1.0],
        [-1.0, 4.0, -1.0],
        [-1.0, -1.0, 5.0],
    ]
    # Check row-sum positivity and sign pattern numerically.
    numeric_holds = (
        A[0][0] > 0 and A[1][1] > 0 and A[2][2] > 0 and
        A[0][1] < 0 and A[0][2] < 0 and A[1][0] < 0 and A[1][2] < 0 and A[2][0] < 0 and A[2][1] < 0 and
        sum(A[0]) > 0 and sum(A[1]) > 0 and sum(A[2]) > 0
    )
    # Determinant is nonzero, so the only solution to A x = 0 is x = 0.
    detA = (
        A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
        - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
        + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0])
    )
    numeric_solution_unique = numeric_holds and detA != 0.0
    checks.append(
        {
            "name": "numerical_sanity_example",
            "passed": bool(numeric_solution_unique),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Concrete example matrix has row sums {sum(A[0])}, {sum(A[1])}, {sum(A[2])} and determinant {detA}; nonzero determinant confirms only the trivial solution.",
        }
    )
    if not numeric_solution_unique:
        proved_all = False

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)