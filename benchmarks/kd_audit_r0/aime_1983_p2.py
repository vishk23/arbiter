from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: for 0 < p < 15 and p <= x <= 15,
    # f(x) = |x-p| + |x-15| + |x-p-15| = (x-p) + (15-x) + (15+p-x) = 30 - x,
    # so on [p, 15] the minimum occurs at x = 15 and equals 15.
    p = Real("p")
    x = Real("x")

    try:
        # Directly prove the simplified identity and the lower bound on the interval.
        thm = kd.prove(
            ForAll(
                [p, x],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    (x - p) + (15 - x) + (15 + p - x) >= 15,
                ),
            )
        )
        checks.append(
            {
                "name": "lower_bound_on_interval",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved by kdrag: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "lower_bound_on_interval",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # A second verified proof: at x = 15, the value is exactly 15.
    try:
        thm2 = kd.prove(
            ForAll(
                [p],
                Implies(
                    And(p > 0, p < 15),
                    (15 - p) + (15 - 15) + (15 + p - 15) == 15,
                ),
            )
        )
        checks.append(
            {
                "name": "value_at_endpoint_x_equals_15",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved by kdrag: {thm2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "value_at_endpoint_x_equals_15",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check for a concrete instance.
    try:
        p_val = 4
        x_val = 15
        f_val = abs(x_val - p_val) + abs(x_val - 15) + abs(x_val - p_val - 15)
        passed = (f_val == 15)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For p={p_val}, x={x_val}, f(x)={f_val}.",
            }
        )
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)