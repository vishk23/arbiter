from fractions import Fraction
from math import prod

import kdrag as kd
from kdrag.smt import *
from sympy import Rational


# Helper: exact finite product as a rational number, for numerical sanity checks.
def finite_product(n: int) -> Fraction:
    p = Fraction(1, 1)
    for k in range(1, n + 1):
        p *= Fraction(1, 1) + Fraction(1, 2**k)
    return p


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof 1: explicit induction-style base cases for n = 1,2,3,
    # and the stronger bound at n=3. These are exact rational inequalities.
    try:
        n1 = finite_product(1)
        n2 = finite_product(2)
        n3 = finite_product(3)
        base_ok = (n1 < Fraction(5, 2)) and (n2 < Fraction(5, 2))
        stronger_base_ok = n3 < Fraction(5, 2) * (1 - Fraction(1, 2**3))
        proof_expr = And(
            RealVal("3/2") < RealVal("5/2"),
            RealVal("15/8") < RealVal("5/2"),
            RealVal("135/64") < RealVal("35/16"),
        )
        proof = kd.prove(proof_expr)
        passed = base_ok and stronger_base_ok and isinstance(proof, kd.Proof)
        checks.append({
            "name": "base_cases_and_stronger_base_n3",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Exact rational base checks for n=1,2 and strengthened base n=3, with a kd.prove certificate.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "base_cases_and_stronger_base_n3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to establish base checks: {e}",
        })
        proved = False

    # Verified proof 2: the inductive algebraic step used in the hint.
    # For x > 0, (1 - x)(1 + x/2) = 1 - x/2 - x^2/2 < 1 - x/2.
    # This is encoded as a universal inequality over reals.
    try:
        x = Real("x")
        inductive_step = ForAll(
            [x],
            Implies(
                x > 0,
                (1 - x) * (1 + x / 2) < (1 - x / 2),
            ),
        )
        proof2 = kd.prove(inductive_step)
        passed = isinstance(proof2, kd.Proof)
        checks.append({
            "name": "inductive_step_algebraic_inequality",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "Verified the strict inequality (1-x)(1+x/2) < 1-x/2 for x>0, which is the key induction algebra.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "inductive_step_algebraic_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove inductive step inequality: {e}",
        })
        proved = False

    # Numerical sanity check: a concrete instance well below 5/2.
    try:
        n = 8
        val = finite_product(n)
        passed = val < Fraction(5, 2)
        checks.append({
            "name": "numerical_sanity_n8",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Exact product for n={n} is {val}, which is < 5/2.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_n8",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}",
        })
        proved = False

    # Optional exact symbolic check of a concrete finite product using SymPy rational arithmetic.
    try:
        exact_n3 = Rational(1, 1)
        for k in range(1, 4):
            exact_n3 *= (1 + Rational(1, 2**k))
        passed = exact_n3 < Rational(5, 2)
        checks.append({
            "name": "sympy_exact_concrete_n3",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy exact arithmetic gives n=3 product = {exact_n3}, which is < 5/2.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "sympy_exact_concrete_n3",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy exact arithmetic check failed: {e}",
        })
        proved = False

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)