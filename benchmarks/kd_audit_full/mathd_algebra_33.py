from fractions import Fraction

import kdrag as kd
from kdrag.smt import *

from sympy import Rational


def verify():
    checks = []
    proved = True

    # Verified proof: encode the algebraic relations in Z3 and prove z/x = 7/25.
    try:
        x, y, z = Reals("x y z")
        thm = kd.prove(
            ForAll(
                [x, y, z],
                Implies(
                    And(2 * x == 5 * y, 7 * y == 10 * z, x != 0, y != 0),
                    z * 25 == 7 * x,
                ),
            )
        )
        checks.append(
            {
                "name": "algebraic_relation_proved",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "algebraic_relation_proved",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Symbolic certificate-like check using exact rational arithmetic.
    try:
        ratio = Rational(2, 5) * Rational(7, 10)
        passed = ratio == Rational(7, 25)
        checks.append(
            {
                "name": "symbolic_fraction_multiplication",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Exact rational computation gives {ratio}, expected 7/25.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "symbolic_fraction_multiplication",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check with concrete values: choose x=25, then y=10, z=7.
    try:
        x0 = 25.0
        y0 = 10.0
        z0 = 7.0
        passed = abs(2 * x0 - 5 * y0) < 1e-12 and abs(7 * y0 - 10 * z0) < 1e-12 and abs(z0 / x0 - 7 / 25) < 1e-12
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"With x={x0}, y={y0}, z={z0}, z/x={z0/x0}.",
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
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)