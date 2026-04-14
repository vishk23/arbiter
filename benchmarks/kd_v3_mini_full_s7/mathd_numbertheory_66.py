import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof: 194 = 17 * 11 + 7, hence 194 ≡ 7 (mod 11)
    try:
        thm = kd.prove(194 == 17 * 11 + 7)
        checks.append(
            {
                "name": "division_identity_194",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified equality: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "division_identity_194",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to certify equality 194 = 17*11 + 7: {e}",
            }
        )
        return {"proved": False, "checks": checks}

    # Formal modular arithmetic check in Z3-encodable form.
    try:
        r = Int("r")
        mod_thm = kd.prove(Exists([r], And(194 == 11 * r + 7, r == 17)))
        checks.append(
            {
                "name": "exists_quotient_for_194_mod_11",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified existence of quotient 17: {mod_thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "exists_quotient_for_194_mod_11",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to certify modular decomposition: {e}",
            }
        )

    # Numerical sanity check
    remainder = 194 % 11
    num_passed = remainder == 7
    checks.append(
        {
            "name": "numerical_remainder_check",
            "passed": num_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"194 % 11 = {remainder}",
        }
    )
    proved = proved and num_passed

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)