from sympy import Rational, simplify

import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Verified symbolic/certificate-style check via exact arithmetic in SymPy.
    # This is a rigorous exact simplification, not a numerical approximation.
    name = "compute_f_of_f_of_1"
    try:
        f = lambda t: Rational(1, 1) / (t + 2)
        expr = simplify(f(f(Rational(1, 1))))
        passed = expr == Rational(3, 7)
        checks.append(
            {
                "name": name,
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Exact simplification gives f(f(1)) = {expr}; expected 3/7.",
            }
        )
        proved = proved and passed
    except Exception as e:
        checks.append(
            {
                "name": name,
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computation failed: {e}",
            }
        )
        proved = False

    # kdrag-backed proof of the arithmetic identity using exact rationals.
    name = "kdrag_exact_arithmetic_certificate"
    try:
        # Encode the exact statement: 1 / (1/3 + 2) = 3/7
        thm = kd.prove(
            Rational(1, 1) / (Rational(1, 3) + 2) == Rational(3, 7)
        )
        passed = thm is not None
        checks.append(
            {
                "name": name,
                "passed": passed,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned a proof object: {thm}.",
            }
        )
        proved = proved and passed
    except Exception as e:
        checks.append(
            {
                "name": name,
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {e}",
            }
        )
        proved = False

    # Numerical sanity check at concrete values (exact rational evaluation).
    name = "numerical_sanity_check"
    try:
        val = float((Rational(1, 1) / (Rational(1, 3) + 2)).evalf())
        passed = abs(val - float(Rational(3, 7))) < 1e-12
        checks.append(
            {
                "name": name,
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Floating-point sanity check: value={val}, target={float(Rational(3, 7))}.",
            }
        )
        proved = proved and passed
    except Exception as e:
        checks.append(
            {
                "name": name,
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())