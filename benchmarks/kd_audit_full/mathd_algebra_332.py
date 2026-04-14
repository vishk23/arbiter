from sympy import Symbol, Rational
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Verified proof: from x+y=14 and xy=19, deduce x^2+y^2=158
    try:
        x = Real("x")
        y = Real("y")
        thm = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(x + y == 14, x * y == 19),
                    x * x + y * y == 158,
                ),
            )
        )
        checks.append(
            {
                "name": "algebraic_identity_from_mean_and_gmean",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "algebraic_identity_from_mean_and_gmean",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {e}",
            }
        )

    # Numerical sanity check at a concrete assignment satisfying the conditions: x=9, y=5
    try:
        xv = 9
        yv = 5
        lhs_mean = (xv + yv) / 2
        lhs_gmean_sq = xv * yv
        lhs_sum_sq = xv * xv + yv * yv
        passed = (lhs_mean == 7) and (lhs_gmean_sq == 19) and (lhs_sum_sq == 158)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"mean={(xv+yv)/2}, xy={xv*yv}, x^2+y^2={lhs_sum_sq}",
            }
        )
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)