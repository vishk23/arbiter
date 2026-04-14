from fractions import Fraction

import kdrag as kd
from kdrag.smt import *

from sympy import Integer, Rational


def verify():
    checks = []
    proved = True

    # Verified proof using kdrag: after factoring out 2^2012, the expression simplifies to 5/3.
    # We encode the core arithmetic identity in Z3-encodable form.
    try:
        a = Int("a")
        expr_thm = kd.prove(
            ForAll(
                [a],
                Implies(
                    a >= 0,
                    (2**(a + 2) + 2**a) * 3 == (2**(a + 2) - 2**a) * 5,
                ),
            )
        )
        checks.append(
            {
                "name": "algebraic_factorization_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {expr_thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "algebraic_factorization_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete exponent 2012.
    try:
        num = Fraction(2**2014 + 2**2012, 2**2014 - 2**2012)
        passed = num == Fraction(5, 3)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical_evaluation",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed exactly as Fraction: {num}, expected 5/3.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_evaluation",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    # Additional symbolic check of the simplified closed form.
    try:
        val = Rational(2**2 + 1, 2**2 - 1)
        passed = val == Rational(5, 3)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "symbolic_simplification",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"SymPy Rational simplification gives {val}.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "symbolic_simplification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"SymPy check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)