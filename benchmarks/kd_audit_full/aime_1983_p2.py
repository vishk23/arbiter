from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: on the interval p <= x <= 15, the absolute values simplify.
    # Let a = x - p, b = 15 - x, c = 15 + p - x.
    # Under p <= x <= 15 and 0 < p < 15, all three are nonnegative, so
    # f(x) = a + b + c = 30 - x, whose minimum on [p, 15] occurs at x = 15,
    # giving 15.
    x = Real("x")
    p = Real("p")

    try:
        thm = kd.prove(
            ForAll(
                [p, x],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    (abs(x - p) + abs(x - 15) + abs(x - p - 15)) == (30 - x),
                ),
            )
        )
        checks.append(
            {
                "name": "absolute_values_reduce_to_linear_expression",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "absolute_values_reduce_to_linear_expression",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof attempt failed: {type(e).__name__}: {e}",
            }
        )

    # Certified inequality proof that 30 - x >= 15 on the interval x <= 15.
    try:
        thm2 = kd.prove(
            ForAll(
                [x],
                Implies(x <= 15, (30 - x) >= 15),
            )
        )
        checks.append(
            {
                "name": "linear_expression_lower_bound",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {thm2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "linear_expression_lower_bound",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof attempt failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete point: p=3, x=15 gives f(15)=15.
    p0 = 3.0
    x0 = 15.0
    f0 = abs(x0 - p0) + abs(x0 - 15.0) + abs(x0 - p0 - 15.0)
    num_pass = (f0 == 15.0)
    checks.append(
        {
            "name": "numerical_sanity_at_x_equals_15",
            "passed": num_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For p={p0}, x={x0}, f(x)={f0}; expected 15.",
        }
    )
    if not num_pass:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)