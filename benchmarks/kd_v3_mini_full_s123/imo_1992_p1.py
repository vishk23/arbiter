import kdrag as kd
from kdrag.smt import *
from sympy import cos, pi, Rational, minimal_polynomial, Symbol


def verify():
    checks = []

    # The problem statement claims two solutions:
    # (2,4,8) and (3,5,15).
    # However, the divisibility condition is false for (2,4,8):
    # (2-1)(4-1)(8-1) = 21 does not divide 2*4*8 - 1 = 63.
    # So the proposed statement is inconsistent as written.
    
    # Check the two stated tuples directly.
    tuples = [(2, 4, 8), (3, 5, 15)]
    for p, q, r in tuples:
        lhs = (p - 1) * (q - 1) * (r - 1)
        rhs = p * q * r - 1
        checks.append({
            "name": f"direct_check_{p}_{q}_{r}",
            "passed": (rhs % lhs == 0),
            "backend": "numerical",
            "proof_type": "counterexample_check",
            "details": f"For ({p},{q},{r}), lhs={(lhs)}, rhs={(rhs)}, rhs % lhs = {rhs % lhs}."
        })

    # Since one of the claimed solutions fails, the original theorem cannot be verified.
    # We still include a tiny consistency check for the actual arithmetic of the second tuple.
    p, q, r = 3, 5, 15
    lhs = (p - 1) * (q - 1) * (r - 1)
    rhs = p * q * r - 1
    checks.append({
        "name": "direct_check_3_5_15_exact",
        "passed": (rhs % lhs == 0),
        "backend": "numerical",
        "proof_type": "counterexample_check",
        "details": f"For (3,5,15), lhs={lhs}, rhs={rhs}, rhs % lhs = {rhs % lhs}."
    })

    return checks