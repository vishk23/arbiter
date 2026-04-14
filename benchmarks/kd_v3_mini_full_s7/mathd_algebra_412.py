import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved_all = True

    # Verified proof: from x + y = 25 and x - y = 11, derive x = 18.
    x, y = Ints("x y")
    theorem = ForAll(
        [x, y],
        Implies(
            And(x + y == 25, x - y == 11, x > y),
            x == 18,
        ),
    )
    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "larger_number_equals_18",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved: {proof}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "larger_number_equals_18",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete solution x=18, y=7.
    x0, y0 = 18, 7
    numerical_ok = (x0 + y0 == 25) and (x0 - y0 == 11) and (x0 > y0) and (x0 == 18)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": numerical_ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked x=18, y=7: sum={x0 + y0}, diff={x0 - y0}, larger={x0}.",
        }
    )
    if not numerical_ok:
        proved_all = False

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)