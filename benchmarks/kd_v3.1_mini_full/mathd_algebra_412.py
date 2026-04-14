import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: from x + y = 25 and x - y = 11, show x = 18.
    x, y = Ints("x y")
    theorem = ForAll(
        [x, y],
        Implies(
            And(x + y == 25, x - y == 11),
            x == 18,
        ),
    )
    try:
        prf = kd.prove(theorem)
        checks.append(
            {
                "name": "algebraic_solution_is_18",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {prf}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "algebraic_solution_is_18",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete solution x=18, y=7.
    x0, y0 = 18, 7
    numeric_ok = (x0 + y0 == 25) and (x0 - y0 == 11) and (x0 == 18)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(numeric_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked x=18, y=7: x+y={x0+y0}, x-y={x0-y0}.",
        }
    )
    if not numeric_ok:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)