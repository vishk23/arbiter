import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Certified algebraic proof: completing the square gives radius^2 = 25.
    x, y = Reals('x y')
    try:
        thm = kd.prove(
            ForAll([x, y],
                   x*x + 8*x + y*y - 6*y == (x + 4)*(x + 4) + (y - 3)*(y - 3) - 25)
        )
        # If kd.prove succeeds, thm is a genuine Proof object.
        details = f"kdrag proved the completed-square identity: {thm}"
        kdrag_ok = True
    except Exception as e:
        kdrag_ok = False
        details = f"kdrag proof failed: {e}"
    checks.append({
        "name": "completed_square_identity",
        "passed": kdrag_ok,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })
    proved = proved and kdrag_ok

    # Certified algebraic proof with SymPy: the radius is exactly 5 because 25 = 5^2.
    X = sp.Symbol('X')
    expr = sp.Integer(25) - sp.Integer(5) ** 2
    try:
        mp = sp.minimal_polynomial(expr, X)
        sympy_ok = (mp == X)
        details = f"minimal_polynomial(25 - 5**2, X) returned {mp}; this certifies the expression is exactly zero."
    except Exception as e:
        sympy_ok = False
        details = f"SymPy certificate failed: {e}"
    checks.append({
        "name": "radius_is_five_symbolic_zero",
        "passed": sympy_ok,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    })
    proved = proved and sympy_ok

    # Numerical sanity check: substitute a concrete point on the circle.
    # Since (x+4)^2 + (y-3)^2 = 25, the point (-9, 3) lies on the circle.
    x0, y0 = -9, 3
    lhs = x0**2 + 8*x0 + y0**2 - 6*y0
    num_ok = (lhs == 0)
    checks.append({
        "name": "numerical_sanity_point_on_circle",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At (-9, 3), x^2 + 8x + y^2 - 6y = {lhs}, so the point lies on the circle.",
    })
    proved = proved and bool(num_ok)

    # Final conclusion: equation is (x+4)^2 + (y-3)^2 = 25, so radius = 5.
    return {
        "proved": proved,
        "checks": checks,
    }


if __name__ == "__main__":
    result = verify()
    print(result)