import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Check 1: Verified certificate that 24 * 116 == 1 mod 121 via explicit arithmetic.
    try:
        b = Int("b")
        thm = kd.prove((24 * 116) % (11 ** 2) == 1)
        checks.append({
            "name": "mod_inverse_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "mod_inverse_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}"
        })

    # Check 2: Verified certificate that 116 is in the correct residue range 0..120.
    try:
        thm2 = kd.prove(And(0 <= 116, 116 < 11 ** 2))
        checks.append({
            "name": "residue_range_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm2}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "residue_range_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {e}"
        })

    # Numerical sanity check.
    try:
        lhs = 24 * 116
        rhs = 1 + 121 * 23
        passed = (lhs == rhs) and (lhs % 121 == 1)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"24*116={lhs}, and 24*116 % 121 = {lhs % 121}; expected 1."
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)