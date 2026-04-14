from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, If


# The theorem concerns a piecewise-linear expression over reals.
# We prove the key simplification and the minimum value on [p, 15].


def _proof_expr_linear():
    p = Real("p")
    x = Real("x")
    expr = If(x - p >= 0, x - p, p - x) + If(x - 15 >= 0, x - 15, 15 - x) + If(x - p - 15 >= 0, x - p - 15, 15 + p - x)
    # On the interval p <= x <= 15, all three absolute values simplify as in the hint.
    thm = kd.prove(
        ForAll(
            [p, x],
            Implies(
                And(p > 0, p < 15, x >= p, x <= 15),
                expr == 30 - x,
            ),
        )
    )
    return thm


def _proof_minimum_value():
    p = Real("p")
    x = Real("x")
    # Since expr = 30 - x on [p, 15], the minimum occurs at x = 15 with value 15.
    thm = kd.prove(
        ForAll(
            [p, x],
            Implies(
                And(p > 0, p < 15, x >= p, x <= 15),
                15 <= 30 - x,
            ),
        )
    )
    return thm


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof check 1: algebraic simplification on the interval.
    try:
        proof1 = _proof_expr_linear()
        checks.append(
            {
                "name": "simplify_absolute_values_on_interval",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned Proof: {proof1}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "simplify_absolute_values_on_interval",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Verified proof check 2: lower bound implying minimum value 15 on the interval.
    try:
        proof2 = _proof_minimum_value()
        checks.append(
            {
                "name": "minimum_value_is_15",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned Proof: {proof2}",
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
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity checks.
    def f_val(x: float, p: float) -> float:
        return abs(x - p) + abs(x - 15.0) + abs(x - p - 15.0)

    try:
        p0 = 4.0
        v_at_15 = f_val(15.0, p0)
        v_at_p = f_val(p0, p0)
        ok = abs(v_at_15 - 15.0) < 1e-12 and abs(v_at_p - 30.0) < 1e-12
        if not ok:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For p={p0}, f(15)={v_at_15}, f(p)={v_at_p}; expected f(15)=15 and f(p)=30.",
            }
        )
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