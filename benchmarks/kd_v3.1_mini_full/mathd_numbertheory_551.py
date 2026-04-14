import kdrag as kd
from kdrag.smt import Int, ForAll, Implies


def verify():
    checks = []
    proved = True

    # Verified proof: 1529 = 6*254 + 5, so 1529 mod 6 = 5.
    try:
        thm = kd.prove(1529 == 6 * 254 + 5)
        checks.append({
            "name": "decomposition_1529_as_6_times_254_plus_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified equality proof obtained: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "decomposition_1529_as_6_times_254_plus_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove the decomposition needed for modular arithmetic: {e}",
        })

    # Verified modular claim derived from the decomposition.
    try:
        x = Int("x")
        mod_thm = kd.prove(1529 % 6 == 5)
        checks.append({
            "name": "remainder_of_1529_mod_6_is_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified modular arithmetic proof obtained: {mod_thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "remainder_of_1529_mod_6_is_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 1529 % 6 == 5 directly: {e}",
        })

    # Numerical sanity check.
    try:
        remainder = 1529 % 6
        passed = (remainder == 5)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed 1529 % 6 = {remainder}; expected 5.",
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
            "details": f"Numerical evaluation failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())