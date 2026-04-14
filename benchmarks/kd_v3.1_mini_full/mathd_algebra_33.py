from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
from sympy import Rational, symbols, simplify


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof: encode the algebraic relations and prove the ratio identity.
    x, y, z = Reals("x y z")
    theorem = ForAll(
        [x, y, z],
        Implies(
            And(2 * x == 5 * y, 7 * y == 10 * z, x != 0, y != 0),
            z / x == Rational(7, 25),
        ),
    )
    try:
        prf = kd.prove(theorem)
        checks.append(
            {
                "name": "algebraic_ratio_theorem",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned Proof: {prf}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "algebraic_ratio_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove theorem with kdrag: {type(e).__name__}: {e}",
            }
        )

    # SymPy exact symbolic check of the ratio computation.
    try:
        ratio = Rational(7, 10) / Rational(5, 2)
        passed = simplify(ratio - Rational(7, 25)) == 0
        checks.append(
            {
                "name": "sympy_exact_ratio",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Computed ratio = {ratio}; simplify(ratio - 7/25) == 0 is {passed}.",
            }
        )
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_exact_ratio",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete nonzero assignment satisfying the equations.
    try:
        x0 = Fraction(25, 2)
        y0 = Fraction(5, 1)
        z0 = Fraction(7, 2)
        eq1 = 2 * x0 == 5 * y0
        eq2 = 7 * y0 == 10 * z0
        ratio_num = Fraction(z0, x0)
        passed = eq1 and eq2 and ratio_num == Fraction(7, 25)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": (
                    f"Using x={x0}, y={y0}, z={z0}: 2x=5y is {eq1}, 7y=10z is {eq2}, "
                    f"z/x={ratio_num}.")
            }
        )
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)