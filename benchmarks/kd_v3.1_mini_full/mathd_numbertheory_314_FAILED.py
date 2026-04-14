import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Constants
    a = IntVal(1342)
    m = IntVal(13)
    ans = IntVal(6710)

    # Check 1: exact remainder r = 1342 mod 13 = 3.
    # We prove this with kdrag as a certificate-style arithmetic fact.
    try:
        r_thm = kd.prove(a % m == IntVal(3))
        checks.append({
            "name": "remainder_of_1342_mod_13_is_3",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified that 1342 % 13 = 3: {r_thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "remainder_of_1342_mod_13_is_3",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify 1342 % 13 = 3: {e}",
        })

    # Check 2: 6710 = 5 * 1342, hence it is a multiple of 1342.
    try:
        mult_thm = kd.prove(ans == IntVal(5) * a)
        checks.append({
            "name": "6710_is_5_times_1342",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified that 6710 = 5*1342: {mult_thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "6710_is_5_times_1342",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify 6710 = 5*1342: {e}",
        })

    # Check 3: 6710 has remainder 0 upon division by 13, which is smaller than r = 3.
    try:
        rem_thm = kd.prove(ans % m == IntVal(0))
        checks.append({
            "name": "6710_mod_13_is_zero",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified that 6710 % 13 = 0: {rem_thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "6710_mod_13_is_zero",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify 6710 % 13 = 0: {e}",
        })

    # Check 4: numerical sanity check with concrete values.
    try:
        r = 1342 % 13
        cond = (6710 % 1342 == 0) and (6710 % 13 < r)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(cond),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"1342 % 13 = {r}, 6710 % 1342 = {6710 % 1342}, 6710 % 13 = {6710 % 13}",
        })
        if not cond:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)