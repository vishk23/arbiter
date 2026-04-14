from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Ints, Real, ForAll, Implies, And


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []

    # Variables are real-valued in the statement.
    a = Real("a")
    b = Real("b")
    x = Real("x")
    y = Real("y")

    # Helper quantities from the standard AIME telescoping trick.
    # S = x + y, P = xy
    S = x + y
    P = x * y

    # Verified proof 1: derive S and P from the given system.
    # We encode the linear consequences directly and prove the unique solution.
    try:
        thm_sp = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(
                        7 * (x + y) == 16 + 3 * (x * y),
                        16 * (x + y) == 42 + 7 * (x * y),
                    ),
                    And(x + y == -14, x * y == -38),
                ),
            )
        )
        checks.append(
            {
                "name": "derive_S_and_P",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Derived S = x + y = -14 and P = x*y = -38. Proof: {thm_sp}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "derive_S_and_P",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the intermediate system for S and P: {e}",
            }
        )

    # Verified proof 2: once S and P are known, the target value is forced.
    try:
        thm_target = kd.prove(
            ForAll(
                [a, b, x, y],
                Implies(
                    And(
                        a * x + b * y == 3,
                        a * x**2 + b * y**2 == 7,
                        a * x**3 + b * y**3 == 16,
                        a * x**4 + b * y**4 == 42,
                        x + y == -14,
                        x * y == -38,
                    ),
                    a * x**5 + b * y**5 == 20,
                ),
            )
        )
        checks.append(
            {
                "name": "target_value",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved ax^5 + by^5 = 20 from the recurrences and S, P. Proof: {thm_target}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "target_value",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the final value: {e}",
            }
        )

    # Numerical sanity check on a concrete consistent instance:
    # choose x=2, y=-10 so S=-8, P=-20, then solve for a,b from the first two equations.
    # This is only a sanity check, not the proof.
    try:
        x0 = 2.0
        y0 = -10.0
        # Solve a*x + b*y = 3 and a*x^2 + b*y^2 = 7
        # 2a - 10b = 3
        # 4a + 100b = 7
        # => b = 1/20, a = 4
        a0 = 4.0
        b0 = 0.05
        lhs1 = a0 * x0 + b0 * y0
        lhs2 = a0 * x0**2 + b0 * y0**2
        lhs3 = a0 * x0**3 + b0 * y0**3
        lhs4 = a0 * x0**4 + b0 * y0**4
        lhs5 = a0 * x0**5 + b0 * y0**5
        passed_num = (
            abs(lhs1 - 3.0) < 1e-9
            and abs(lhs2 - 7.0) < 1e-9
            and abs(lhs3 - 16.0) < 1e-9
            and abs(lhs4 - 42.0) < 1e-9
            and abs(lhs5 - 20.0) < 1e-9
        )
        checks.append(
            {
                "name": "numerical_sanity",
                "passed": passed_num,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Concrete check at (a,b,x,y)=({a0},{b0},{x0},{y0}) gives values ({lhs1}, {lhs2}, {lhs3}, {lhs4}, {lhs5}).",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)