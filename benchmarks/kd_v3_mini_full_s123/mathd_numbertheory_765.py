import kdrag as kd
from kdrag.smt import *
from sympy import mod_inverse


def verify():
    checks = []

    # Check 1: 24 is invertible mod 1199, and its inverse is 50.
    try:
        inv = mod_inverse(24, 1199)
        passed = (inv == 50)
        checks.append({
            "name": "modular_inverse_certificate",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "computation",
            "details": f"mod_inverse(24, 1199) = {inv}",
        })
    except Exception as e:
        checks.append({
            "name": "modular_inverse_certificate",
            "passed": False,
            "backend": "sympy",
            "proof_type": "computation",
            "details": f"mod_inverse failed: {e}",
        })

    # Check 2: solve 24x ≡ 15 (mod 1199).
    try:
        inv = mod_inverse(24, 1199)
        x_mod = (inv * 15) % 1199
        largest_negative = x_mod - 1199
        passed = (x_mod == 750 and largest_negative == -449)
        checks.append({
            "name": "solve_congruence_symbolically",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "computation",
            "details": f"x ≡ {x_mod} (mod 1199), so largest negative representative is {largest_negative}",
        })
    except Exception as e:
        checks.append({
            "name": "solve_congruence_symbolically",
            "passed": False,
            "backend": "sympy",
            "proof_type": "computation",
            "details": f"computation failed: {e}",
        })

    # Check 3: direct verification that -449 satisfies the congruence.
    try:
        lhs = (24 * (-449) - 15) % 1199
        passed = (lhs == 0)
        checks.append({
            "name": "verify_answer_minus_449",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "congruence_check",
            "details": f"(24 * -449 - 15) % 1199 = {lhs}",
        })
    except Exception as e:
        checks.append({
            "name": "verify_answer_minus_449",
            "passed": False,
            "backend": "sympy",
            "proof_type": "congruence_check",
            "details": f"verification failed: {e}",
        })

    return checks