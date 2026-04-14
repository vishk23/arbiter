import math
import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified certificate-style proof in kdrag that the completed-square
    # transformation is algebraically equivalent to the original equation.
    x = Real("x")
    y = Real("y")
    lhs = x * x + 8 * x + y * y - 6 * y
    rhs = (x + 4) * (x + 4) + (y - 3) * (y - 3) - 25
    thm1 = None
    try:
        thm1 = kd.prove(ForAll([x, y], lhs == rhs))
        checks.append(
            {
                "name": "complete_square_equivalence",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm1}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "complete_square_equivalence",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Verified symbolic algebra in SymPy showing the square-completed form.
    sx, sy = sp.symbols('x y', real=True)
    expr = sx**2 + 8*sx + sy**2 - 6*sy
    completed = sp.expand((sx + 4)**2 + (sy - 3)**2 - 25)
    sympy_ok = sp.expand(expr - completed) == 0
    checks.append(
        {
            "name": "sympy_completing_the_square",
            "passed": bool(sympy_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "SymPy expansion shows x^2+8x+y^2-6y == (x+4)^2+(y-3)^2-25.",
        }
    )
    if not sympy_ok:
        proved = False

    # Check 3: Numerical sanity check at a concrete point on the circle.
    # Center is (-4, 3), radius 5; point (1, 3) should satisfy the equation.
    xv, yv = 1, 3
    val = xv * xv + 8 * xv + yv * yv - 6 * yv
    num_ok = (val == 0)
    checks.append(
        {
            "name": "numerical_sanity_point_on_circle",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Substituting (1,3) gives {val}; expected 0.",
        }
    )
    if not num_ok:
        proved = False

    # Check 4: Numerical sanity check for the radius value itself.
    radius = math.sqrt(25)
    rad_ok = (radius == 5)
    checks.append(
        {
            "name": "radius_evaluates_to_five",
            "passed": bool(rad_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"sqrt(25) evaluates to {radius}.",
        }
    )
    if not rad_ok:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)