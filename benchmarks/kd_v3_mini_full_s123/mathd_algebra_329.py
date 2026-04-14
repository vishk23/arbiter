import kdrag as kd
from kdrag.smt import Ints, ForAll, Implies, And


def verify():
    checks = []

    # Verified proof: solve the linear system exactly in Z3.
    x, y = Ints("x y")
    theorem = ForAll(
        [x, y],
        Implies(
            And(x == 3 * y, 2 * x + 5 * y == 11),
            x + y == 4,
        ),
    )
    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "linear_system_implies_sum_is_4",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {proof}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "linear_system_implies_sum_is_4",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete solution (3, 1).
    x_val, y_val = 3, 1
    numeric_ok = (x_val == 3 * y_val) and (2 * x_val + 5 * y_val == 11) and (x_val + y_val == 4)
    checks.append(
        {
            "name": "numerical_sanity_check_solution_3_1",
            "passed": bool(numeric_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked (x, y) = ({x_val}, {y_val}): x=3y, 2x+5y=11, and x+y=4.",
        }
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)