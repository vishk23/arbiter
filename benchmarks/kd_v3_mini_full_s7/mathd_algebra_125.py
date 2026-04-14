import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []

    # Verified proof: encode the age constraints in Z3 and prove the son's age is 6.
    x, y = Ints("x y")
    theorem = ForAll(
        [x, y],
        Implies(
            And(y == 5 * x, (x - 3) + (y - 3) == 30),
            x == 6,
        ),
    )
    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "age_equations_imply_son_age_6",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved by kd.prove; certificate: {proof}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "age_equations_imply_son_age_6",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete solution x=6, y=30.
    x_val = 6
    y_val = 30
    sanity = (y_val == 5 * x_val) and ((x_val - 3) + (y_val - 3) == 30)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(sanity),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked x=6, y=30: y=5x is {y_val == 5 * x_val}, and three-years-ago sum is {((x_val - 3) + (y_val - 3))}.",
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)