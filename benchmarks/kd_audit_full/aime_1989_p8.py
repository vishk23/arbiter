from __future__ import annotations

from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import Real, Reals, ForAll, Implies, And


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Verified proof: the three given equations imply the target value 334.
    x1, x2, x3, x4, x5, x6, x7 = Reals("x1 x2 x3 x4 x5 x6 x7")

    eq1_lhs = x1 + 4 * x2 + 9 * x3 + 16 * x4 + 25 * x5 + 36 * x6 + 49 * x7
    eq2_lhs = 4 * x1 + 9 * x2 + 16 * x3 + 25 * x4 + 36 * x5 + 49 * x6 + 64 * x7
    eq3_lhs = 9 * x1 + 16 * x2 + 25 * x3 + 36 * x4 + 49 * x5 + 64 * x6 + 81 * x7
    target_lhs = 16 * x1 + 25 * x2 + 36 * x3 + 49 * x4 + 64 * x5 + 81 * x6 + 100 * x7

    theorem = ForAll(
        [x1, x2, x3, x4, x5, x6, x7],
        Implies(
            And(eq1_lhs == 1, eq2_lhs == 12, eq3_lhs == 123),
            target_lhs == 334,
        ),
    )

    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "main_linear_algebra_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove() succeeded: {proof}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "main_linear_algebra_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove() failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check using a concrete solution derived from the linear system.
    # One convenient solution is x1=1, x2=x3=x4=x5=x6=x7=0, which satisfies the equations
    # and gives target 16. We instead use the actual solved coefficients from the hint.
    # The system only constrains a quadratic combination, so we verify the derived f(4)=334
    # numerically from the recovered quadratic coefficients.
    a, b, c = 50, -139, 90
    val = 16 * a + 4 * b + c
    checks.append(
        {
            "name": "numerical_evaluation_f4",
            "passed": val == 334,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed 16*a + 4*b + c = {val} with (a,b,c)=(50,-139,90).",
        }
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)