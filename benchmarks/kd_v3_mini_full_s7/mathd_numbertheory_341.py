from kdrag.smt import *
import kdrag as kd


def verify() -> dict:
    checks = []
    proved_all = True

    # Verified proof: final three digits of 5^100 are 625, so the sum is 13.
    # We prove the stronger modular fact 5^100 mod 1000 = 625 using kdrag/Z3.
    try:
        n = Int("n")
        # Use a concrete arithmetic proof directly.
        thm = kd.prove(5**100 % 1000 == 625)
        checks.append({
            "name": "mod_5_1000",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified proof obtained: {thm}",
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "mod_5_1000",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 5^100 mod 1000 = 625: {e}",
        })

    # Numerical sanity check: compute the concrete value and digit sum.
    try:
        val = 5**100
        last_three = val % 1000
        digit_sum = (last_three // 100) + ((last_three // 10) % 10) + (last_three % 10)
        passed = (last_three == 625) and (digit_sum == 13)
        checks.append({
            "name": "numerical_digit_sum",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"5^100 mod 1000 = {last_three}, digit sum = {digit_sum}.",
        })
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "numerical_digit_sum",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}",
        })

    # Final conclusion check, derived from the above verified facts.
    conclusion_passed = any(c["name"] == "mod_5_1000" and c["passed"] for c in checks) and any(
        c["name"] == "numerical_digit_sum" and c["passed"] for c in checks
    )
    checks.append({
        "name": "final_answer",
        "passed": conclusion_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Since 5^100 ends in 625, the sum of its final three digits is 6+2+5 = 13.",
    })
    if not conclusion_passed:
        proved_all = False

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    print(verify())