import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Certified proof: from the geometric conditions, derive the exact coordinates
    # and the distance-squared to the origin.
    x, y = Reals('x y')

    try:
        thm = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(
                        x < 0,
                        y < 0,
                        y == -6,
                        (x - 8) * (x - 8) + (y - 3) * (y - 3) == 225,
                    ),
                    x * x + y * y == 52,
                ),
            )
        )
        checks.append(
            {
                "name": "geometric_conditions_imply_distance_squared_52",
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
                "name": "geometric_conditions_imply_distance_squared_52",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {e}",
            }
        )

    # Certified proof of the arithmetic step: if x < 0 and (x-8)^2 = 144, then x = -4.
    x = Real('x')
    try:
        thm2 = kd.prove(
            ForAll(
                [x],
                Implies(
                    And(x < 0, (x - 8) * (x - 8) == 144),
                    x == -4,
                ),
            )
        )
        checks.append(
            {
                "name": "negative_root_of_quadratic_is_minus_four",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm2),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "negative_root_of_quadratic_is_minus_four",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {e}",
            }
        )

    # Numerical sanity check at the concrete solution (-4, -6).
    try:
        x0, y0 = -4, -6
        d_axis = abs(y0)
        d_point = ((x0 - 8) ** 2 + (y0 - 3) ** 2) ** 0.5
        d_origin_sq = x0 * x0 + y0 * y0
        passed = (d_axis == 6) and (abs(d_point - 15.0) < 1e-12) and (d_origin_sq == 52)
        checks.append(
            {
                "name": "numerical_sanity_at_solution",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At (-4,-6): dist_to_x_axis={d_axis}, dist_to_(8,3)={d_point}, origin_distance_squared={d_origin_sq}.",
            }
        )
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_at_solution",
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