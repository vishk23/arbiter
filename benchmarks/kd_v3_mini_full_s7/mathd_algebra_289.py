from sympy import Integer
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Check 1: algebraic consistency for the forced quadratic factorization.
    # If k and t are the two positive integer roots of x^2 - m x + n = 0,
    # then k + t = m and k t = n. Since n is prime and k,t are positive integers,
    # one of k,t must be 1. With k > t, we get t = 1 and k = n.
    try:
        k, t, m, n = Ints('k t m n')
        claim = ForAll(
            [k, t, m, n],
            Implies(
                And(k > 0, t > 0, m > 0, n > 1, k + t == m, k * t == n),
                Or(t == 1, k == 1)
            )
        )
        proof1 = kd.prove(claim)
        checks.append({
            "name": "prime_product_forces_factor_one",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(proof1)
        })
    except Exception as e:
        checks.append({
            "name": "prime_product_forces_factor_one",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Could not certify the factorization claim in kdrag: {e}"
        })

    # Check 2: evaluate the expression at the forced solution m=3, n=2, k=2, t=1.
    m = Integer(3)
    nval = Integer(2)
    kval = Integer(2)
    tval = Integer(1)
    expr = m**nval + nval**m + kval**tval + tval**kval
    num_passed = expr == 20
    checks.append({
        "name": "numerical_evaluation_at_forced_values",
        "passed": bool(num_passed),
        "backend": "numerical",
        "proof_type": "computation",
        "details": f"Computed value: {expr}"
    })

    return checks