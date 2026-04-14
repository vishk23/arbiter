from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
from sympy import I, Rational, simplify


def verify() -> dict:
    checks = []
    all_passed = True

    # Verified proof: algebraic identity for the complex current.
    try:
        a, b = Ints('a b')
        # Encode the real and imaginary parts of (1+i)/(2-i) after rationalization.
        # We prove: (1+i)/(2-i) = 1/5 + 3/5*i by checking the exact complex multiplication.
        # Let I = a + b*i, and verify that (2-i) * (1/5 + 3/5*i) = 1+i.
        thm = kd.prove(
            And(
                (2 * RatVal(1, 5) - (-1) * RatVal(3, 5)) == 1,
                (2 * RatVal(3, 5) + (-1) * RatVal(1, 5)) == 1,
            )
        )
        # The above is a certificate-backed proof of the rationalized product equations.
        # Since Z3 does not directly encode complex numbers here, this certificate suffices
        # to verify the claimed decomposition of the quotient.
        checks.append(
            {
                "name": "algebraic_certificate_for_current",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned Proof: {thm}",
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "algebraic_certificate_for_current",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # SymPy symbolic verification of the exact quotient.
    try:
        V = 1 + I
        Z = 2 - I
        I_current = simplify(V / Z)
        passed = (I_current == Rational(1, 5) + Rational(3, 5) * I)
        if not passed:
            all_passed = False
        checks.append(
            {
                "name": "sympy_exact_quotient",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"simplify((1+I)/(2-I)) -> {I_current}",
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "sympy_exact_quotient",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at concrete values.
    try:
        lhs = complex(1, 1) / complex(2, -1)
        rhs = complex(1 / 5, 3 / 5)
        passed = abs(lhs - rhs) < 1e-12
        if not passed:
            all_passed = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"lhs={lhs}, rhs={rhs}, abs diff={abs(lhs-rhs)}",
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": all_passed, "checks": checks}


if __name__ == "__main__":
    print(verify())