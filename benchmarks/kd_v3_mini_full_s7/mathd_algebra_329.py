import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified proof: solve the linear system with Z3/Knuckledragger.
    x, y = Ints("x y")
    theorem = ForAll(
        [x, y],
        Implies(And(x == 3 * y, 2 * x + 5 * y == 11), x + y == 4),
    )
    try:
        prf = kd.prove(theorem)
        checks.append(
            {
                "name": "linear_system_sum_is_4",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {prf}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "linear_system_sum_is_4",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete solution (3,1).
    x_val = 3
    y_val = 1
    sanity = (3 * y_val == x_val) and (2 * x_val + 5 * y_val == 11) and (x_val + y_val == 4)
    checks.append(
        {
            "name": "numerical_sanity_at_solution",
            "passed": bool(sanity),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked (x,y)=({x_val},{y_val}); equations and sum evaluate to True.",
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)