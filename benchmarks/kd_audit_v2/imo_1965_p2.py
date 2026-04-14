from itertools import permutations

import kdrag as kd
from kdrag.smt import *


def _coeff_conditions(a11, a12, a13, a21, a22, a23, a31, a32, a33):
    return And(
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


def _eqs(a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3):
    return And(
        a11 * x1 + a12 * x2 + a13 * x3 == 0,
        a21 * x1 + a22 * x2 + a23 * x3 == 0,
        a31 * x1 + a32 * x2 + a33 * x3 == 0,
    )


def _weakly_sorted_lemma():
    x1, x2, x3 = Reals("x1 x2 x3")
    a31, a32, a33 = Reals("a31 a32 a33")
    thm = kd.prove(
        ForAll(
            [x1, x2, x3, a31, a32, a33],
            Implies(
                And(
                    x1 >= 0,
                    x2 >= 0,
                    x3 >= 0,
                    x1 <= x2,
                    x2 <= x3,
                    a31 < 0,
                    a32 < 0,
                    a33 > 0,
                    a31 + a32 + a33 > 0,
                ),
                a31 * x1 + a32 * x2 + a33 * x3 > 0,
            ),
        )
    )
    return thm


def _weakly_sorted_negative_lemma():
    x1, x2, x3 = Reals("x1 x2 x3")
    a31, a32, a33 = Reals("a31 a32 a33")
    thm = kd.prove(
        ForAll(
            [x1, x2, x3, a31, a32, a33],
            Implies(
                And(
                    x1 <= 0,
                    x2 <= 0,
                    x3 <= 0,
                    x1 >= x2,
                    x2 >= x3,
                    a31 < 0,
                    a32 < 0,
                    a33 > 0,
                    a31 + a32 + a33 > 0,
                ),
                a31 * x1 + a32 * x2 + a33 * x3 < 0,
            ),
        )
    )
    return thm


def _main_theorem():
    a11, a12, a13, a21, a22, a23, a31, a32, a33 = Reals(
        "a11 a12 a13 a21 a22 a23 a31 a32 a33"
    )
    x1, x2, x3 = Reals("x1 x2 x3")
    thm = kd.prove(
        ForAll(
            [a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3],
            Implies(
                And(_coeff_conditions(a11, a12, a13, a21, a22, a23, a31, a32, a33), _eqs(a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3)),
                And(x1 == 0, x2 == 0, x3 == 0),
            ),
        )
    )
    return thm


def verify():
    checks = []
    proved = True

    try:
        lemma1 = _weakly_sorted_lemma()
        checks.append(
            {
                "name": "sorted_positive_row_is_positive",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(lemma1),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sorted_positive_row_is_positive",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove auxiliary positivity lemma: {e}",
            }
        )

    try:
        lemma2 = _weakly_sorted_negative_lemma()
        checks.append(
            {
                "name": "sorted_negative_row_is_negative",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(lemma2),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sorted_negative_row_is_negative",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove auxiliary negativity lemma: {e}",
            }
        )

    try:
        main_thm = _main_theorem()
        checks.append(
            {
                "name": "main_uniqueness_theorem",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(main_thm),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "main_uniqueness_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": (
                    "Could not encode the full contradiction argument directly in Z3 "
                    f"for this standalone module: {e}"
                ),
            }
        )

    # Numerical sanity check: a concrete matrix satisfying the sign conditions
    # and a nontrivial vector should not solve the system.
    a = [
        [3.0, -1.0, -1.0],
        [-2.0, 5.0, -1.0],
        [-1.0, -2.0, 6.0],
    ]
    x = [1.0, 1.0, 1.0]
    residuals = [sum(a[i][j] * x[j] for j in range(3)) for i in range(3)]
    numeric_passed = any(abs(r) > 1e-9 for r in residuals)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": numeric_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Residuals for sample nonzero vector [1,1,1] are {residuals}.",
        }
    )
    proved = proved and numeric_passed

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)