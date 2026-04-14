import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof: the stated hypotheses imply f = -10 and z = 7.
    f, z = Reals("f z")
    try:
        theorem = kd.prove(
            ForAll(
                [f, z],
                Implies(
                    And(f + 3 * z == 11, 3 * (f - 1) - 5 * z == -68),
                    And(f == -10, z == 7),
                ),
            )
        )
        checks.append(
            {
                "name": "linear_system_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(theorem),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "linear_system_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove theorem with kdrag: {e}",
            }
        )

    # Numerical sanity check at the claimed solution.
    f_val, z_val = -10, 7
    lhs1 = f_val + 3 * z_val
    lhs2 = 3 * (f_val - 1) - 5 * z_val
    num_passed = (lhs1 == 11) and (lhs2 == -68)
    checks.append(
        {
            "name": "numerical_sanity_at_solution",
            "passed": num_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Substitution gives equation1={lhs1}, equation2={lhs2}.",
        }
    )
    if not num_passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())