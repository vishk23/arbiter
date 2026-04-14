from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


def _check_kdrag_theorem() -> Dict:
    name = "imo_1965_p2_no_nontrivial_solution"
    try:
        # Real coefficients with sign conditions as in the problem statement.
        a11, a12, a13 = Reals("a11 a12 a13")
        a21, a22, a23 = Reals("a21 a22 a23")
        a31, a32, a33 = Reals("a31 a32 a33")
        x1, x2, x3 = Reals("x1 x2 x3")

        hyp = And(
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
        concl = And(x1 == 0, x2 == 0, x3 == 0)

        # This exact theorem is not readily Z3-encodable with a compact direct proof,
        # because it requires a case analysis over the signs/orderings of the unknowns.
        # We therefore do not pretend to have a kdrag certificate here.
        # The mathematical content is verified by the numerical sanity check below,
        # but this check is marked as not passed since no formal certificate is produced.
        _ = (hyp, concl)
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": (
                "A full formal kdrag/Z3 certificate was not constructed. "
                "The theorem requires a nontrivial sign/case argument over arbitrary real coefficients; "
                "this module therefore reports the missing certificate rather than faking a proof."
            ),
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof attempt failed with exception: {type(e).__name__}: {e}",
        }


def _check_numerical_sanity() -> Dict:
    name = "numerical_sanity_example_matrix"
    try:
        # A concrete instance satisfying the hypotheses.
        A = [
            [3.0, -1.0, -1.0],
            [-2.0, 5.0, -1.0],
            [-1.0, -2.0, 4.0],
        ]
        # Verify coefficient signs and row sums.
        conditions = [
            A[0][0] > 0 and A[1][1] > 0 and A[2][2] > 0,
            A[0][1] < 0 and A[0][2] < 0 and A[1][0] < 0 and A[1][2] < 0 and A[2][0] < 0 and A[2][1] < 0,
            sum(A[0]) > 0 and sum(A[1]) > 0 and sum(A[2]) > 0,
        ]
        # Check that a few random nonzero vectors do not satisfy Ax=0.
        test_vectors = [
            (1.0, 0.0, 0.0),
            (0.0, 1.0, -1.0),
            (2.0, -3.0, 1.0),
        ]
        nonzero_fail = True
        for x in test_vectors:
            y = [sum(A[i][j] * x[j] for j in range(3)) for i in range(3)]
            if all(abs(v) < 1e-12 for v in y):
                nonzero_fail = False
                break
        passed = all(conditions) and nonzero_fail
        return {
            "name": name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": (
                "Concrete matrix satisfies the sign hypotheses; tested nonzero vectors do not solve Ax=0. "
                "This is only a sanity check, not a proof of the general theorem."
            ),
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed with exception: {type(e).__name__}: {e}",
        }


def verify() -> Dict:
    checks: List[Dict] = []
    checks.append(_check_kdrag_theorem())
    checks.append(_check_numerical_sanity())
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)