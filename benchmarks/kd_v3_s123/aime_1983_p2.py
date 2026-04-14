import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof with kdrag that the simplified expression is 30 - x.
    # We encode the key case assumptions on the interval p <= x <= 15 and 0 < p < 15.
    x, p = Reals("x p")
    try:
        thm1 = kd.prove(
            ForAll(
                [x, p],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    And(
                        x - p == Abs(x - p),
                        15 - x == Abs(x - 15),
                        15 + p - x == Abs(x - p - 15),
                    ),
                ),
            )
        )
        checks.append(
            {
                "name": "absolute_value_simplification_on_interval",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kd.prove: {thm1}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "absolute_value_simplification_on_interval",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # Check 2: Verified kdrag proof that the simplified form equals 30 - x.
    try:
        thm2 = kd.prove(
            ForAll(
                [x, p],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    (x - p) + (15 - x) + (15 + p - x) == 30 - x,
                ),
            )
        )
        checks.append(
            {
                "name": "simplified_expression_equals_30_minus_x",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kd.prove: {thm2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "simplified_expression_equals_30_minus_x",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # Check 3: Verified kdrag proof that 30 - x is minimized at x = 15 on [p, 15].
    try:
        thm3 = kd.prove(
            ForAll(
                [x, p],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    30 - x >= 15,
                ),
            )
        )
        checks.append(
            {
                "name": "lower_bound_for_simplified_expression",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kd.prove: {thm3}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "lower_bound_for_simplified_expression",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    # Check 4: Numerical sanity check at a concrete point.
    try:
        p0 = 7.0
        x0 = 15.0
        f0 = abs(x0 - p0) + abs(x0 - 15.0) + abs(x0 - p0 - 15.0)
        expected = 15.0
        passed = abs(f0 - expected) < 1e-9
        checks.append(
            {
                "name": "numerical_sanity_check_at_x_15_p_7",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"f(15) with p=7 gives {f0}, expected {expected}.",
            }
        )
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check_at_x_15_p_7",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )

    # Final check: the claimed minimum value is 15.
    try:
        thm4 = kd.prove(
            ForAll(
                [x, p],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    (x - p) + (15 - x) + (15 + p - x) >= 15,
                ),
            )
        )
        checks.append(
            {
                "name": "minimum_value_is_15",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kd.prove: {thm4}; equality is attained at x=15.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "minimum_value_is_15",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2))