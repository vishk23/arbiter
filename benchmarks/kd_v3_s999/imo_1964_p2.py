from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Real, Reals, ForAll, Implies, And


def _prove_triangle_inequality():
    """Prove a^2(b+c-a)+b^2(c+a-b)+c^2(a+b-c) <= 3abc for triangle sides."""
    x, y, z = Reals("x y z")

    # Triangle sides via the standard substitution:
    # a = x+y, b = x+z, c = y+z with x,y,z >= 0.
    a = x + y
    b = x + z
    c = y + z

    lhs = a * a * (b + c - a) + b * b * (c + a - b) + c * c * (a + b - c)
    rhs = 3 * a * b * c

    # After substitution, the inequality is equivalent to
    # (x^2y + x^2z + y^2x + y^2z + z^2x + z^2y) >= 6xyz,
    # which follows from AM-GM.
    amgm_goal = ForAll(
        [x, y, z],
        Implies(
            And(x >= 0, y >= 0, z >= 0),
            x * x * y + x * x * z + y * y * x + y * y * z + z * z * x + z * z * y >= 6 * x * y * z,
        ),
    )
    amgm_proof = kd.prove(amgm_goal)

    # Original inequality in substituted variables, reduced by algebraic simplification.
    triangle_goal = ForAll(
        [x, y, z],
        Implies(
            And(x >= 0, y >= 0, z >= 0),
            lhs <= rhs,
        ),
    )
    triangle_proof = kd.prove(triangle_goal, by=[amgm_proof])
    return triangle_proof


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Verified proof: AM-GM form used in the standard substitution.
    try:
        proof = _prove_triangle_inequality()
        checks.append(
            {
                "name": "AM-GM reduction after substitution",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(proof),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "AM-GM reduction after substitution",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete triangle.
    try:
        a, b, c = 3.0, 4.0, 5.0
        lhs = a * a * (b + c - a) + b * b * (c + a - b) + c * c * (a + b - c)
        rhs = 3 * a * b * c
        passed = lhs <= rhs + 1e-12
        checks.append(
            {
                "name": "Numerical sanity check at (3,4,5)",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"lhs={lhs}, rhs={rhs}",
            }
        )
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "Numerical sanity check at (3,4,5)",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Evaluation failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)