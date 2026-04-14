from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *


def _abs_piecewise_identity(x):
    """Helper for the three-region absolute value expansion."""
    return If(x <= -1,
              -(x - 1) - x - (x + 1),
              If(x < 0,
                 -(x - 1) - x + (x + 1),
                 If(x <= 1,
                    -(x - 1) + x + (x + 1),
                    (x - 1) + x + (x + 1))))


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Check 1: a verified theorem proving the desired implication directly by case split.
    x = Real("x")
    premise = Abs(x - 1) + Abs(x) + Abs(x + 1) == x + 2
    conclusion = And(x >= 0, x <= 1)
    theorem = ForAll([x], Implies(premise, conclusion))
    try:
        prf = kd.prove(theorem)
        checks.append({
            "name": "main_implication",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a proof: {prf}",
        })
    except Exception as e:
        checks.append({
            "name": "main_implication",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove the implication in kdrag/Z3: {type(e).__name__}: {e}",
        })

    # Check 2: numerical sanity check at a concrete value satisfying the conclusion.
    x0 = 0.5
    lhs0 = abs(x0 - 1) + abs(x0) + abs(x0 + 1)
    rhs0 = x0 + 2
    num_pass = abs(lhs0 - rhs0) < 1e-12 and (0 <= x0 <= 1)
    checks.append({
        "name": "numerical_sanity_x_half",
        "passed": bool(num_pass),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At x={x0}, lhs={lhs0}, rhs={rhs0}, and 0<=x<=1 is {0 <= x0 <= 1}.",
    })

    # Check 3: numerical counterexample sanity outside the interval (shows premise is restrictive).
    x1 = 2.0
    lhs1 = abs(x1 - 1) + abs(x1) + abs(x1 + 1)
    rhs1 = x1 + 2
    num2_pass = abs(lhs1 - rhs1) > 1e-12
    checks.append({
        "name": "numerical_outside_interval",
        "passed": bool(num2_pass),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At x={x1}, lhs={lhs1}, rhs={rhs1}; equality fails as expected.",
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)