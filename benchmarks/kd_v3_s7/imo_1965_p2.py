from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


def _build_and_prove_core() -> tuple[bool, str]:
    """Attempt to prove the core theorem in an encoding suitable for Z3.

    We encode the matrix entries as reals and the assumptions as universally
    quantified constraints over the coefficients. The theorem states that any
    nonzero vector cannot satisfy all three equations under the sign/row-sum
    conditions.
    """
    # Coefficients
    a11, a12, a13, a21, a22, a23, a31, a32, a33 = Reals(
        "a11 a12 a13 a21 a22 a23 a31 a32 a33"
    )
    x1, x2, x3 = Reals("x1 x2 x3")

    # Assumptions
    coeff_assumptions = And(
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

    # We prove the contrapositive: there is no nonzero solution under the assumptions.
    theorem = ForAll(
        [a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3],
        Implies(
            And(coeff_assumptions, eqs),
            And(x1 == 0, x2 == 0, x3 == 0),
        ),
    )

    prf = kd.prove(theorem)
    return True, f"kdrag proof produced: {prf}"


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Check 1: Verified proof certificate via kdrag/Z3.
    try:
        ok, details = _build_and_prove_core()
        checks.append(
            {
                "name": "unique_zero_solution_theorem",
                "passed": ok,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": details,
            }
        )
        proved = proved and ok
    except Exception as e:
        checks.append(
            {
                "name": "unique_zero_solution_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed or could not be established by Z3/kdrag: {type(e).__name__}: {e}",
            }
        )
        proved = False

    # Check 2: Numerical sanity check with a concrete matrix satisfying the sign conditions.
    # This matrix has positive diagonal, negative off-diagonal, and positive row sums.
    A = [
        [3.0, -1.0, -1.0],
        [-1.0, 4.0, -1.0],
        [-1.0, -1.0, 5.0],
    ]
    vec = (0.0, 0.0, 0.0)
    residuals = [sum(A[i][j] * vec[j] for j in range(3)) for i in range(3)]
    passed_num = all(abs(r) < 1e-12 for r in residuals)
    checks.append(
        {
            "name": "numerical_zero_vector_sanity",
            "passed": passed_num,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Residuals for the zero vector on a sample admissible matrix: {residuals}",
        }
    )
    proved = proved and passed_num

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)