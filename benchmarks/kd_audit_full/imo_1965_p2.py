from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


def _proved_check(name: str, proof_obj, details: str) -> Dict:
    return {
        "name": name,
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    }


def _failed_check(name: str, details: str, backend: str = "kdrag", proof_type: str = "certificate") -> Dict:
    return {
        "name": name,
        "passed": False,
        "backend": backend,
        "proof_type": proof_type,
        "details": details,
    }


def verify() -> Dict:
    checks: List[Dict] = []

    # Main theorem: if all coefficients satisfy the sign/sum conditions,
    # then the only solution to Ax = 0 is x = 0.
    a11, a12, a13 = Reals("a11 a12 a13")
    a21, a22, a23 = Reals("a21 a22 a23")
    a31, a32, a33 = Reals("a31 a32 a33")
    x1, x2, x3 = Reals("x1 x2 x3")

    coeff_hyps = And(
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
    )

    eqs = And(
        a11 * x1 + a12 * x2 + a13 * x3 == 0,
        a21 * x1 + a22 * x2 + a23 * x3 == 0,
        a31 * x1 + a32 * x2 + a33 * x3 == 0,
    )

    theorem = ForAll(
        [a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3],
        Implies(And(coeff_hyps, eqs), And(x1 == 0, x2 == 0, x3 == 0)),
    )

    try:
        pf = kd.prove(theorem)
        checks.append(
            _proved_check(
                "main_uniqueness_theorem",
                pf,
                "Z3 proved that any real solution of the 3x3 homogeneous system under the stated sign and row-sum hypotheses must be the zero vector.",
            )
        )
    except Exception as e:
        checks.append(
            _failed_check(
                "main_uniqueness_theorem",
                f"kdrag proof attempt failed: {type(e).__name__}: {e}",
            )
        )

    # Derived contradiction check: if x1=x2=x3=t and row sums are positive, then t=0.
    t = Real("t")
    row1sum, row2sum, row3sum = Reals("row1sum row2sum row3sum")
    common_zero_theorem = ForAll(
        [row1sum, row2sum, row3sum, t],
        Implies(And(row1sum > 0, row2sum > 0, row3sum > 0, row1sum * t == 0, row2sum * t == 0, row3sum * t == 0), t == 0),
    )
    try:
        pf2 = kd.prove(common_zero_theorem)
        checks.append(
            _proved_check(
                "equal_coordinates_imply_zero",
                pf2,
                "Verified that if all three unknowns are equal and each row sum is positive, then the common value must be zero.",
            )
        )
    except Exception as e:
        checks.append(
            _failed_check(
                "equal_coordinates_imply_zero",
                f"kdrag proof attempt failed: {type(e).__name__}: {e}",
            )
        )

    # Numerical sanity check with a concrete admissible matrix.
    # Example matrix satisfying the conditions:
    # [ 2, -1, -1 ]
    # [ -1, 2, -1 ]
    # [ -1, -1, 2 ]
    # Row sums are all 0, so we use a strictly positive-sum perturbation.
    A = [[3.0, -1.0, -1.0], [-1.0, 3.0, -1.0], [-1.0, -1.0, 3.0]]
    # Determinant for this symmetric example is nonzero.
    det = (
        A[0][0] * (A[1][1] * A[2][2] - A[1][2] * A[2][1])
        - A[0][1] * (A[1][0] * A[2][2] - A[1][2] * A[2][0])
        + A[0][2] * (A[1][0] * A[2][1] - A[1][1] * A[2][0])
    )
    numerical_pass = abs(det - 16.0) < 1e-9
    checks.append(
        {
            "name": "numerical_sanity_example_determinant",
            "passed": numerical_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For the concrete admissible matrix [[3,-1,-1],[-1,3,-1],[-1,-1,3]], det={det}; nonzero determinant confirms only the trivial solution in this sample.",
        }
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)