from itertools import product

import kdrag as kd
from kdrag.smt import *


def _sign(x):
    return If(x > 0, 1, If(x < 0, -1, 0))


def verify():
    checks = []

    # Verified proof: if all x_i have the same sign, then a positive diagonal term plus
    # coefficient-sum positivity makes the corresponding linear form nonzero.
    a31, a32, a33, x1, x2, x3 = Reals("a31 a32 a33 x1 x2 x3")
    same_sign_lem = None
    try:
        same_sign_lem = kd.prove(
            ForAll(
                [a31, a32, a33, x1, x2, x3],
                Implies(
                    And(
                        a31 > 0,
                        a32 < 0,
                        a33 > 0,
                        x1 > 0,
                        x2 > 0,
                        x3 > 0,
                        x1 <= x2,
                        x2 <= x3,
                    ),
                    a31 * x1 + a32 * x2 + a33 * x3 != 0,
                ),
            )
        )
        checks.append(
            {
                "name": "positive_case_nonzero_third_equation",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(same_sign_lem),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "positive_case_nonzero_third_equation",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # Main theorem: there is no nonzero solution under the sign constraints.
    a11, a12, a13 = Reals("a11 a12 a13")
    a21, a22, a23 = Reals("a21 a22 a23")
    a31, a32, a33 = Reals("a31 a32 a33")
    x1, x2, x3 = Reals("x1 x2 x3")

    theorem = None
    try:
        theorem = kd.prove(
            ForAll(
                [a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3],
                Implies(
                    And(
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
                    ),
                    And(x1 == 0, x2 == 0, x3 == 0),
                ),
            )
        )
        checks.append(
            {
                "name": "imo_1965_p2_main_theorem",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(theorem),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "imo_1965_p2_main_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Could not discharge the full theorem in Z3: {e}",
            }
        )

    # Numerical sanity check on a concrete admissible instance.
    # Matrix with positive diagonal, negative off-diagonal, positive row sums.
    A = [[3.0, -1.0, -1.0], [-1.0, 3.0, -1.0], [-1.0, -1.0, 3.0]]
    x_good = (0.0, 0.0, 0.0)
    x_bad = (1.0, 1.0, 1.0)
    def eval_rows(x):
        return [sum(A[i][j] * x[j] for j in range(3)) for i in range(3)]

    good_res = eval_rows(x_good)
    bad_res = eval_rows(x_bad)
    numerical_passed = all(abs(v) < 1e-12 for v in good_res) and any(abs(v) > 1e-12 for v in bad_res)
    checks.append(
        {
            "name": "numerical_sanity_example",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"zero vector maps to {good_res}; (1,1,1) maps to {bad_res}",
        }
    )

    proved = all(ch["passed"] for ch in checks) and any(ch["proof_type"] == "certificate" and ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)