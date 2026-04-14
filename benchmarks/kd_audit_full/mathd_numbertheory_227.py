from fractions import Fraction

import kdrag as kd
from kdrag.smt import Int, Ints, And, Or, Implies, ForAll, Exists


def verify():
    checks = []

    # Verified proof: the algebraic relation forces n = 5 for positive x,y.
    try:
        x, y, n = Ints("x y n")
        theorem = ForAll(
            [x, y, n],
            Implies(
                And(
                    x > 0,
                    y > 0,
                    n > 0,
                    3 * x * (n - 4) == 2 * y * (6 - n),
                ),
                n == 5,
            ),
        )
        pf = kd.prove(theorem)
        checks.append(
            {
                "name": "algebraic_relation_implies_family_size_five",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {pf}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "algebraic_relation_implies_family_size_five",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Additional verified proof: if n=5 then the equation is satisfiable with positive x,y.
    # Take x=6, y=1, then 3*x*(5-4)=2*y*(6-5)=18? Wait, that's not equal.
    # Instead choose any positive x,y satisfying 3x = 2y, e.g. x=2, y=3.
    try:
        x, y = Ints("x y")
        theorem2 = Exists(
            [x, y],
            And(x > 0, y > 0, 3 * x * (5 - 4) == 2 * y * (6 - 5)),
        )
        pf2 = kd.prove(theorem2)
        checks.append(
            {
                "name": "existence_of_positive_solution_for_n_five",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {pf2}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "existence_of_positive_solution_for_n_five",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check from the original fractions: if n=5, the relation becomes 3x=2y.
    # Example with x=2, y=3 gives x/4 + y/6 = 1 and (x+y)/5 = 1.
    x_val = Fraction(2, 1)
    y_val = Fraction(3, 1)
    lhs = x_val / 4 + y_val / 6
    rhs = (x_val + y_val) / 5
    numerical_passed = lhs == rhs and lhs == 1
    checks.append(
        {
            "name": "numerical_sanity_check_example_x2_y3_n5",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For x=2, y=3, n=5: lhs={lhs}, rhs={rhs}",
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)