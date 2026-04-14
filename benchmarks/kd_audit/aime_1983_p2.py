from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, If


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: Symbolic simplification on the target interval
    # For p <= x <= 15 and 0 < p < 15, the absolute values simplify to:
    # |x-p| = x-p, |x-15| = 15-x, |x-p-15| = 15+p-x, so f(x)=30-x.
    try:
        x = Real("x")
        p = Real("p")
        f = lambda xx, pp: If(xx - pp >= 0, xx - pp, pp - xx) + If(xx - 15 >= 0, xx - 15, 15 - xx) + If(xx - pp - 15 >= 0, xx - pp - 15, 15 + pp - xx)

        thm1 = kd.prove(
            ForAll([x, p],
                   Implies(And(p > 0, p < 15, x >= p, x <= 15),
                           f(x, p) == 30 - x))
        )
        checks.append({
            "name": "absolute_value_simplification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm1)
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "absolute_value_simplification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove symbolic simplification: {e}"
        })

    # Check 2: Minimum value on [p,15] is attained at x = 15 and equals 15
    try:
        x = Real("x")
        p = Real("p")
        thm2 = kd.prove(
            ForAll([x, p],
                   Implies(And(p > 0, p < 15, x >= p, x <= 15),
                           30 - x >= 15))
        )
        checks.append({
            "name": "minimum_value_lower_bound",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm2)
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "minimum_value_lower_bound",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove minimum lower bound: {e}"
        })

    # Check 3: Numerical sanity check with concrete values
    try:
        p_val = 7.0
        x_val = 15.0
        f_val = abs(x_val - p_val) + abs(x_val - 15.0) + abs(x_val - p_val - 15.0)
        passed = abs(f_val - 15.0) < 1e-12
        checks.append({
            "name": "numerical_sanity_at_endpoint",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"With p={p_val}, x={x_val}, f(x)={f_val}, expected 15.0"
        })
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_at_endpoint",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)