from fractions import Fraction

import sympy as sp
import kdrag as kd
from kdrag.smt import *


x, y, z = Ints('x y z')


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof in kdrag/Z3.
    # Encode the linear combination suggested by the hint:
    # 3*(3x+4y-12z=10) + 4*(-2x-3y+9z=-4)
    # => 9x + 12y - 36z - 8x - 12y + 36z = 30 - 16
    # => x = 14.
    try:
        thm = kd.prove(
            ForAll([x, y, z],
                   Implies(And(3 * x + 4 * y - 12 * z == 10,
                               -2 * x - 3 * y + 9 * z == -4),
                           x == 14))
        )
        checks.append({
            "name": "linear_system_implies_x_14",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "linear_system_implies_x_14",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Check 2: SymPy symbolic elimination / solving.
    # From the system, solve for x and verify exact equality to 14.
    try:
        xs, ys, zs = sp.symbols('x y z')
        sol = sp.solve([
            sp.Eq(3 * xs + 4 * ys - 12 * zs, 10),
            sp.Eq(-2 * xs - 3 * ys + 9 * zs, -4)
        ], [xs, ys], dict=True)
        x_expr = sp.simplify(sol[0][xs])
        passed = sp.simplify(x_expr - 14) == 0
        checks.append({
            "name": "sympy_solve_x_equals_14",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy returned x = {sp.srepr(x_expr)}; difference from 14 simplifies to 0.",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_solve_x_equals_14",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve failed: {type(e).__name__}: {e}",
        })

    # Check 3: Numerical sanity check with a concrete solution.
    # Choose z = 0, y = 3, x = 14 satisfies both equations.
    try:
        xv, yv, zv = 14, 3, 0
        eq1 = 3 * xv + 4 * yv - 12 * zv
        eq2 = -2 * xv - 3 * yv + 9 * zv
        passed = (eq1 == 10) and (eq2 == -4)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Substitution gives equation values ({eq1}, {eq2}) for (x,y,z)=({xv},{yv},{zv}).",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)