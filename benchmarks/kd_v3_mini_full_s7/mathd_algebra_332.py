import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified theorem: if x+y=14 and xy=19, then x^2+y^2=158.
    x, y = Reals("x y")
    theorem = ForAll(
        [x, y],
        Implies(And(x + y == 14, x * y == 19), x * x + y * y == 158),
    )
    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "algebraic_identity_from_means",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "algebraic_identity_from_means",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check with concrete values satisfying the constraints:
    # x=7+sqrt(30), y=7-sqrt(30) gives x+y=14 and xy=19.
    import math

    x0 = 7.0 + math.sqrt(30.0)
    y0 = 7.0 - math.sqrt(30.0)
    lhs_mean = (x0 + y0) / 2.0
    lhs_geo_sq = x0 * y0
    lhs_target = x0 * x0 + y0 * y0
    num_pass = (
        abs(lhs_mean - 7.0) < 1e-9
        and abs(lhs_geo_sq - 19.0) < 1e-9
        and abs(lhs_target - 158.0) < 1e-9
    )
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(num_pass),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": (
                f"Using x=7+sqrt(30), y=7-sqrt(30): mean={(x0+y0)/2}, "
                f"product={x0*y0}, x^2+y^2={lhs_target}"
            ),
        }
    )
    if not num_pass:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())