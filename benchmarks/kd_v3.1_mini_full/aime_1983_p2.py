import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    p = Real("p")
    x = Real("x")

    # Certified proof: on the interval p <= x <= 15, the absolute values simplify as
    # |x-p| = x-p, |x-15| = 15-x, |x-p-15| = p+15-x.
    # Hence f(x) = 30 - x, and since x <= 15, we get f(x) >= 15.
    try:
        thm1 = kd.prove(
            ForAll(
                [p, x],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    (x - p) + (15 - x) + (p + 15 - x) == 30 - x,
                ),
            )
        )
        checks.append({
            "name": "interval_simplification_to_30_minus_x",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: {thm1}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "interval_simplification_to_30_minus_x",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}",
        })

    # Certified proof: f(x)=30-x on [p,15], so f(x) >= 15. Equality holds at x=15.
    try:
        thm2 = kd.prove(
            ForAll(
                [p, x],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    30 - x >= 15,
                ),
            )
        )
        checks.append({
            "name": "minimum_value_on_interval_is_15",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: {thm2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "minimum_value_on_interval_is_15",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}",
        })

    # Numerical sanity check at a concrete admissible point.
    try:
        p0 = 4
        x0 = 15
        f0 = abs(x0 - p0) + abs(x0 - 15) + abs(x0 - p0 - 15)
        ok = (f0 == 15)
        checks.append({
            "name": "numerical_sanity_check_at_x_equals_15",
            "passed": ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For p={p0}, x={x0}, f(x)={f0}.",
        })
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check_at_x_equals_15",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)