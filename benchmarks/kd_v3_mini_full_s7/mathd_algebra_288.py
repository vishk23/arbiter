from __future__ import annotations

from typing import Any, Dict, List

import sympy as sp

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved_all = True

    # Check 1: Verified symbolic proof in kdrag/Z3.
    # Formalized claim: if x = -4 and y = -6, then the distance squared to the origin is 52.
    # This is a direct arithmetic certificate for the final value n.
    try:
        x = Real("x")
        y = Real("y")
        thm = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(x == -4, y == -6),
                    x * x + y * y == 52,
                ),
            )
        )
        checks.append(
            {
                "name": "origin_distance_squared_for_point_minus4_minus6",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned a proof certificate: {thm}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "origin_distance_squared_for_point_minus4_minus6",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Symbolic derivation using SymPy.
    # Solve the constraints exactly and extract the negative-coordinate point.
    try:
        x, y = sp.symbols("x y", real=True)
        sol = sp.solve(
            [sp.Eq(sp.Abs(y), 6), sp.Eq((x - 8) ** 2 + (y - 3) ** 2, 15 ** 2)],
            [x, y],
            dict=True,
        )
        sol_neg = [s for s in sol if sp.simplify(s[x]).is_real and sp.simplify(s[y]).is_real and sp.N(s[x]) < 0 and sp.N(s[y]) < 0]
        if not sol_neg:
            raise ValueError(f"No solution with both coordinates negative found from {sol}")
        chosen = sol_neg[0]
        n_val = sp.simplify(chosen[x] ** 2 + chosen[y] ** 2)
        passed = bool(n_val == 52)
        if passed:
            details = f"Exact solve returned point {chosen}; distance squared to origin simplifies to {n_val}."
        else:
            proved_all = False
            details = f"Exact solve returned point {chosen}; distance squared simplified to {n_val}, not 52."
        checks.append(
            {
                "name": "sympy_exact_solution_and_n",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": details,
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "sympy_exact_solution_and_n",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic derivation failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Numerical sanity check at the concrete point (-4, -6).
    try:
        xv = -4
        yv = -6
        dist_to_x_axis = abs(yv)
        dist_to_point_83 = ((xv - 8) ** 2 + (yv - 3) ** 2) ** 0.5
        dist_to_origin_sq = xv * xv + yv * yv
        passed = (dist_to_x_axis == 6) and (abs(dist_to_point_83 - 15) < 1e-12) and (dist_to_origin_sq == 52)
        if not passed:
            proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": (
                    f"For (-4,-6): distance to x-axis = {dist_to_x_axis}, "
                    f"distance to (8,3) = {dist_to_point_83}, distance^2 to origin = {dist_to_origin_sq}."
                ),
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)