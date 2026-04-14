from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, If, Solver, sat


def _abs_expr(x, a):
    return If(x >= a, x - a, a - x)


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: On the interval p <= x <= 15, each absolute value simplifies,
    # and the expression becomes 30 - x, hence its minimum is at x = 15 and equals 15.
    try:
        p = Real("p")
        x = Real("x")
        f = _abs_expr(x, p) + _abs_expr(x, 15) + _abs_expr(x, p + 15)

        # Prove the simplification on the interval p <= x <= 15.
        simp_thm = kd.prove(
            ForAll(
                [p, x],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    f == (x - p) + (15 - x) + (15 + p - x),
                ),
            )
        )

        # Prove that the simplified expression is minimized at x=15 on [p,15].
        min_thm = kd.prove(
            ForAll(
                [p, x],
                Implies(
                    And(p > 0, p < 15, x >= p, x <= 15),
                    (30 - x) >= 15,
                ),
            )
        )

        checks.append(
            {
                "name": "absolute-value-simplification",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {simp_thm}",
            }
        )
        checks.append(
            {
                "name": "minimum-lower-bound",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {min_thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "absolute-value-simplification",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete value.
    try:
        p_val = 4.0
        x_val = 15.0
        f_val = abs(x_val - p_val) + abs(x_val - 15.0) + abs(x_val - p_val - 15.0)
        ok = abs(f_val - 15.0) < 1e-9
        checks.append(
            {
                "name": "numerical-sanity-at-x-equals-15",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For p={p_val}, x={x_val}, f(x)={f_val}.",
            }
        )
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical-sanity-at-x-equals-15",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    # Direct witness check: at x=15, the value is 15 for any p in (0,15).
    try:
        p_val = 7.5
        x_val = 15.0
        f_val = abs(x_val - p_val) + abs(x_val - 15.0) + abs(x_val - p_val - 15.0)
        ok = abs(f_val - 15.0) < 1e-9
        checks.append(
            {
                "name": "witness-value-at-x-equals-15",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For p={p_val}, x={x_val}, f(x)={f_val}, matching the claimed minimum 15.",
            }
        )
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "witness-value-at-x-equals-15",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical witness check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)