from __future__ import annotations

import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved_all = True

    # Certified proof: the given linear system forces x = 14.
    try:
        x, y, z = Reals("x y z")
        thm = kd.prove(
            ForAll(
                [x, y, z],
                Implies(
                    And(
                        3 * x + 4 * y - 12 * z == 10,
                        -2 * x - 3 * y + 9 * z == -4,
                    ),
                    x == 14,
                ),
            )
        )
        checks.append(
            {
                "name": "linear_system_implies_x_equals_14",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proved: {thm}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "linear_system_implies_x_equals_14",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Additional certified proof: the system is consistent with x = 14.
    # We exhibit one concrete solution family instance, e.g. z = 0, y = -8.
    try:
        x, y, z = Reals("x y z")
        inst = kd.prove(
            And(
                3 * 14 + 4 * (-8) - 12 * 0 == 10,
                -2 * 14 - 3 * (-8) + 9 * 0 == -4,
            )
        )
        checks.append(
            {
                "name": "concrete_solution_sanity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag verified concrete instance: {inst}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "concrete_solution_sanity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag concrete-instance proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: evaluate the equations at the certified solution.
    try:
        xv, yv, zv = 14.0, -8.0, 0.0
        lhs1 = 3 * xv + 4 * yv - 12 * zv
        lhs2 = -2 * xv - 3 * yv + 9 * zv
        passed = abs(lhs1 - 10.0) < 1e-12 and abs(lhs2 + 4.0) < 1e-12 and abs(xv - 14.0) < 1e-12
        checks.append(
            {
                "name": "numerical_sanity_at_x_14",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"lhs1={lhs1}, lhs2={lhs2}, x={xv}",
            }
        )
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_at_x_14",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)