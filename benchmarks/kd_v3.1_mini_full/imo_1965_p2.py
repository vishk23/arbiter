from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


def _prove_row_max_lemma():
    # Lemma: for a single row with positive row-sum, if xk is maximal among x1,x2,x3
    # and all row coefficients satisfy a_kk > 0, a_kj < 0 for j != k, then
    # sum_j a_kj x_j >= xk * sum_j a_kj.
    # This is the key order-based inequality used in the proof.
    a0, a1, a2, x0, x1, x2 = Reals("a0 a1 a2 x0 x1 x2")
    prem = And(a0 > 0, a1 < 0, a2 < 0, x0 >= x1, x0 >= x2)
    lhs = a0 * x0 + a1 * x1 + a2 * x2
    rhs = x0 * (a0 + a1 + a2)
    # Since a1,a2 < 0 and x1,x2 <= x0, we get a1*x1 >= a1*x0 and a2*x2 >= a2*x0.
    # Z3 can prove the linear inequality directly.
    return kd.prove(ForAll([a0, a1, a2, x0, x1, x2], Implies(prem, lhs >= rhs)))


def _prove_row_min_lemma():
    # Symmetric lemma for a minimal component: if x0 is minimal and row-sum positive,
    # then sum_j a_kj x_j <= x0 * sum_j a_kj.
    a0, a1, a2, x0, x1, x2 = Reals("a0 a1 a2 x0 x1 x2")
    prem = And(a0 > 0, a1 < 0, a2 < 0, x0 <= x1, x0 <= x2)
    lhs = a0 * x0 + a1 * x1 + a2 * x2
    rhs = x0 * (a0 + a1 + a2)
    return kd.prove(ForAll([a0, a1, a2, x0, x1, x2], Implies(prem, lhs <= rhs)))


def _prove_trivial_solution_theorem():
    # Formal theorem: under the matrix sign pattern and positive row sums,
    # Ax = 0 implies x = 0.
    a11, a12, a13 = Reals("a11 a12 a13")
    a21, a22, a23 = Reals("a21 a22 a23")
    a31, a32, a33 = Reals("a31 a32 a33")
    x1, x2, x3 = Reals("x1 x2 x3")

    row1 = And(a11 > 0, a12 < 0, a13 < 0, a11 + a12 + a13 > 0)
    row2 = And(a21 < 0, a22 > 0, a23 < 0, a21 + a22 + a23 > 0)
    row3 = And(a31 < 0, a32 < 0, a33 > 0, a31 + a32 + a33 > 0)
    system = And(
        a11 * x1 + a12 * x2 + a13 * x3 == 0,
        a21 * x1 + a22 * x2 + a23 * x3 == 0,
        a31 * x1 + a32 * x2 + a33 * x3 == 0,
    )

    # The core theorem is a linear arithmetic fact; Z3 should discharge it.
    thm = ForAll(
        [a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3],
        Implies(
            And(row1, row2, row3, system),
            And(x1 == 0, x2 == 0, x3 == 0),
        ),
    )
    return kd.prove(thm)


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved_all = True

    # Verified proof 1: order-based inequality lemma for a maximal component.
    try:
        p1 = _prove_row_max_lemma()
        checks.append(
            {
                "name": "row_max_inequality_lemma",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified Proof object: {p1}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "row_max_inequality_lemma",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Verified proof 2: symmetric minimal-component lemma.
    try:
        p2 = _prove_row_min_lemma()
        checks.append(
            {
                "name": "row_min_inequality_lemma",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified Proof object: {p2}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "row_min_inequality_lemma",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Verified proof 3: full theorem.
    try:
        p3 = _prove_trivial_solution_theorem()
        checks.append(
            {
                "name": "imo_1965_p2_trivial_solution",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified Proof object: {p3}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "imo_1965_p2_trivial_solution",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: a concrete example satisfying the hypotheses should only
    # have the zero solution. We check that a nonzero candidate does not satisfy Ax=0.
    try:
        A = [
            [3, -1, -1],
            [-2, 5, -1],
            [-1, -2, 4],
        ]
        x_nonzero = [1, -1, 0]
        residual = [sum(A[i][j] * x_nonzero[j] for j in range(3)) for i in range(3)]
        passed = residual != [0, 0, 0]
        if not passed:
            proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Example residual for x={x_nonzero} is {residual}; nonzero candidate is not a solution.",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)