from dataclasses import dataclass
from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


# Variables for symbolic theorem statement
x1, x2, x3 = Reals("x1 x2 x3")

# Coefficients of the 3x3 system
A = [[Real(f"a{i}{j}") for j in range(1, 4)] for i in range(1, 4)]

def system_eqs(x1, x2, x3):
    return [
        A[0][0] * x1 + A[0][1] * x2 + A[0][2] * x3 == 0,
        A[1][0] * x1 + A[1][1] * x2 + A[1][2] * x3 == 0,
        A[2][0] * x1 + A[2][1] * x2 + A[2][2] * x3 == 0,
    ]


def assumptions():
    # (a) diagonal positive
    diag_pos = And(A[0][0] > 0, A[1][1] > 0, A[2][2] > 0)
    # (b) remaining coefficients negative
    off_neg = And(
        A[0][1] < 0, A[0][2] < 0,
        A[1][0] < 0, A[1][2] < 0,
        A[2][0] < 0, A[2][1] < 0,
    )
    # (c) each row sum positive
    row_sum_pos = And(
        A[0][0] + A[0][1] + A[0][2] > 0,
        A[1][0] + A[1][1] + A[1][2] > 0,
        A[2][0] + A[2][1] + A[2][2] > 0,
    )
    return And(diag_pos, off_neg, row_sum_pos)


# Main theorem: any solution must be trivial.
# We encode the contrapositive-style fact that no nonzero solution exists.
# This is a Z3-encodable linear-arithmetic claim.
main_thm = ForAll(
    [A[0][0], A[0][1], A[0][2], A[1][0], A[1][1], A[1][2], A[2][0], A[2][1], A[2][2], x1, x2, x3],
    Implies(
        And(
            assumptions(),
            *system_eqs(x1, x2, x3),
        ),
        And(x1 == 0, x2 == 0, x3 == 0),
    ),
)


def _prove_main():
    # Z3 proves the universally quantified linear statement.
    return kd.prove(main_thm)


# A simpler certificate-backed lemma used for verification bookkeeping:
# if all three variables are equal and the row sums are positive, then common value must be zero.
# This is a key algebraic step in the human proof and is Z3-encodable.
y = Real("y")
row_sums = [A[i][0] + A[i][1] + A[i][2] for i in range(3)]
all_equal_implies_zero = ForAll(
    [A[0][0], A[0][1], A[0][2], A[1][0], A[1][1], A[1][2], A[2][0], A[2][1], A[2][2], y],
    Implies(
        And(
            A[0][0] > 0, A[1][1] > 0, A[2][2] > 0,
            A[0][1] < 0, A[0][2] < 0, A[1][0] < 0, A[1][2] < 0, A[2][0] < 0, A[2][1] < 0,
            row_sums[0] > 0, row_sums[1] > 0, row_sums[2] > 0,
            A[0][0] * y + A[0][1] * y + A[0][2] * y == 0,
            A[1][0] * y + A[1][1] * y + A[1][2] * y == 0,
            A[2][0] * y + A[2][1] * y + A[2][2] * y == 0,
        ),
        y == 0,
    ),
)


def verify() -> Dict:
    checks: List[Dict] = []
    proved = True

    # Verified proof 1: the main theorem via kdrag / Z3.
    try:
        pf = _prove_main()
        checks.append({
            "name": "main_theorem_no_nonzero_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded with proof object: {pf}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "main_theorem_no_nonzero_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Verified proof 2: key equal-variables lemma.
    try:
        pf2 = kd.prove(all_equal_implies_zero)
        checks.append({
            "name": "equal_variables_force_zero",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded with proof object: {pf2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "equal_variables_force_zero",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check: a concrete matrix satisfying the sign conditions.
    # We verify that the only solution is trivial by checking determinant nonzero.
    try:
        import sympy as sp
        M = sp.Matrix([
            [3, -1, -1],
            [-2, 4, -1],
            [-1, -1, 5],
        ])
        detM = sp.factor(M.det())
        passed_num = detM != 0
        checks.append({
            "name": "numerical_sanity_concrete_matrix_nonzero_determinant",
            "passed": bool(passed_num),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Concrete matrix determinant = {detM}; nonzero determinant confirms only trivial solution for this instance.",
        })
        proved = proved and bool(passed_num)
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_concrete_matrix_nonzero_determinant",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical/symbolic sanity check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)