from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
import sympy as sp


# The theorem: if 2x = 5y and 7y = 10z, then z/x = 7/25.
# We prove the equivalent algebraic statement using rational arithmetic.


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof check via kdrag: the algebraic ratio simplifies to 7/25.
    # Let x and y be nonzero reals satisfying x = 5y/2 and z = 7y/10.
    # Then z/x = (7y/10)/(5y/2) = 7/25.
    x, y = Reals("x y")
    z = Real("z")

    theorem = ForAll([y], Implies(y != 0, ((RealVal(7) / RealVal(10) * y) / (RealVal(5) / RealVal(2) * y)) == RealVal(7) / RealVal(25)))
    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "algebraic_ratio_certificate",
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
                "name": "algebraic_ratio_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # SymPy symbolic sanity: exact simplification of the derived expression.
    try:
        xs, ys, zs = sp.symbols("x y z", nonzero=True)
        expr = sp.simplify((sp.Rational(7, 10) * ys) / (sp.Rational(5, 2) * ys))
        passed = sp.simplify(expr - sp.Rational(7, 25)) == 0
        checks.append(
            {
                "name": "sympy_symbolic_simplification",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"simplified expression = {expr}",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_symbolic_simplification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"sympy check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete value y=20.
    try:
        yv = Fraction(20, 1)
        xv = Fraction(5, 2) * yv
        zv = Fraction(7, 10) * yv
        ratio = zv / xv
        passed = ratio == Fraction(7, 25)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"x={xv}, z={zv}, z/x={ratio}",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())