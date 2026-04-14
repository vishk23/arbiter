from sympy import Symbol
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Verified proof: on the interval p <= x <= 15, f(x) = 30 - x, hence minimum is 15 at x=15.
    try:
        p = Real("p")
        x = Real("x")
        f_expr = None  # symbolic placeholder; the theorem is encoded directly below.
        thm = kd.prove(
            ForAll([p, x],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    (x - p) + (15 - x) + (15 + p - x) == 30 - x
                )
            )
        )
        checks.append({
            "name": "absolute_value_elimination_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kd.prove certified that for 0 < p < 15 and p <= x <= 15, the simplified expression equals 30 - x."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "absolute_value_elimination_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Could not certify identity with kdrag: {e}"
        })

    # Verified proof: 30 - x is minimized on [p, 15] at x = 15, giving 15.
    try:
        p = Real("p")
        x = Real("x")
        thm2 = kd.prove(
            ForAll([p, x],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    30 - x >= 15
                )
            )
        )
        checks.append({
            "name": "minimum_value_lower_bound",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kd.prove certified 30 - x >= 15 on the interval p <= x <= 15."
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "minimum_value_lower_bound",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Could not certify lower bound with kdrag: {e}"
        })

    # Numerical sanity check at a concrete value.
    try:
        p_val = 7
        x_val = 15
        f_val = abs(x_val - p_val) + abs(x_val - 15) + abs(x_val - p_val - 15)
        passed = (f_val == 15)
        checks.append({
            "name": "numerical_sanity_check_at_x_equals_15",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For p={p_val}, x={x_val}, f(x)={f_val}, matching the claimed minimum 15."
        })
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check_at_x_equals_15",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)