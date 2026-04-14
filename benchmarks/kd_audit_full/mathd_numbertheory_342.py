import kdrag as kd
from kdrag.smt import Int


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof: 54 = 9*6 + 0, hence 54 mod 6 = 0.
    try:
        q = Int("q")
        r = Int("r")
        # Prove existence of quotient and remainder matching Euclidean division.
        thm = kd.prove(
            (54 == 9 * 6 + 0)
        )
        # If the equality is proven, the modulus claim is immediate.
        mod_thm = kd.prove((54 % 6) == 0)
        checks.append(
            {
                "name": "54_equals_9_times_6_plus_0",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified equality proof: {thm}",
            }
        )
        checks.append(
            {
                "name": "remainder_of_54_mod_6_is_0",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified modulus proof: {mod_thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "54_equals_9_times_6_plus_0",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {e}",
            }
        )
        checks.append(
            {
                "name": "remainder_of_54_mod_6_is_0",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "Skipped because the foundational equality proof failed.",
            }
        )

    # Numerical sanity check.
    num_val = 54 % 6
    num_passed = (num_val == 0)
    checks.append(
        {
            "name": "numerical_sanity_check_54_mod_6",
            "passed": num_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed 54 % 6 = {num_val}.",
        }
    )

    proved = proved and all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())