import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: establish the exact remainder of 2^2010 modulo 10.
    # Since 2^n mod 10 has period 4, and 2010 = 4*502 + 2, the remainder is 4.
    try:
        n = Int("n")
        thm = kd.prove(2**2010 % 10 == 4)
        checks.append({
            "name": "units_digit_of_2_to_2010",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded with proof: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "units_digit_of_2_to_2010",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check
    try:
        val = pow(2, 2010, 10)
        passed = (val == 4)
        checks.append({
            "name": "numerical_sanity_mod_10",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"pow(2, 2010, 10) = {val}",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_mod_10",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical check failed: {type(e).__name__}: {e}",
        })

    # Additional verified symbolic check: 2010 mod 4 = 2
    try:
        rem = 2010 % 4
        passed = (rem == 2)
        checks.append({
            "name": "exponent_remainder_mod_4",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"2010 % 4 = {rem}",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "exponent_remainder_mod_4",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"remainder check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)