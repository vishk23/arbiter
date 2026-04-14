import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Main verified theorem: every integer solution forces the target value 588.
    try:
        x, y = Ints("x y")
        theorem = ForAll(
            [x, y],
            Implies(
                y * y + 3 * x * x * y * y == 30 * x * x + 517,
                3 * x * x * y * y == 588,
            ),
        )
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "main_diophantine_theorem",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(proof),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "main_diophantine_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Auxiliary verified theorem: there actually are integer solutions, e.g. x=2, y=7.
    try:
        ex_thm = Exists(
            [x, y],
            And(
                y * y + 3 * x * x * y * y == 30 * x * x + 517,
                3 * x * x * y * y == 588,
            ),
        )
        ex_proof = kd.prove(ex_thm)
        checks.append(
            {
                "name": "existence_of_solution",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(ex_proof),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "existence_of_solution",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag existential proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check using the concrete solution from the factorization hint.
    try:
        xv = 2
        yv = 7
        lhs = yv * yv + 3 * xv * xv * yv * yv
        rhs = 30 * xv * xv + 517
        target = 3 * xv * xv * yv * yv
        passed = (lhs == rhs) and (target == 588)
        checks.append(
            {
                "name": "numerical_sanity_at_x_2_y_7",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For (x,y)=({xv},{yv}): lhs={lhs}, rhs={rhs}, 3*x^2*y^2={target}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_at_x_2_y_7",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(c["passed"] for c in checks) and any(
        c["passed"] and c["proof_type"] == "certificate" for c in checks
    )
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())