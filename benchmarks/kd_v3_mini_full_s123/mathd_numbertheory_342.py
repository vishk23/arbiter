import kdrag as kd
from kdrag.smt import Int, IntVal, ForAll, Implies


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof: 54 = 9*6 + 0, hence 54 mod 6 = 0.
    try:
        q = IntVal(9)
        r = IntVal(0)
        thm = kd.prove(54 == q * 6 + r)
        checks.append({
            "name": "division_identity_54",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified identity: 54 = 9*6 + 0. Proof: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "division_identity_54",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify identity 54 = 9*6 + 0: {e}",
        })

    # Verified theorem: modulo remainder is 0.
    try:
        thm2 = kd.prove(54 % 6 == 0)
        checks.append({
            "name": "remainder_54_mod_6",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified remainder statement 54 % 6 == 0. Proof: {thm2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "remainder_54_mod_6",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify 54 % 6 == 0: {e}",
        })

    # Numerical sanity check.
    remainder = 54 % 6
    num_passed = (remainder == 0)
    checks.append({
        "name": "numerical_sanity_remainder",
        "passed": num_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed 54 % 6 = {remainder}.",
    })
    if not num_passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)