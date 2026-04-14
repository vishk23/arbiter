import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: 123456 = 101*1222 + 34, hence 123456 ≡ 34 (mod 101).
    try:
        n = Int("n")
        thm = kd.prove(
            Exists(
                [n],
                And(
                    n >= 0,
                    n < 101,
                    123456 % 101 == n,
                    n == 34,
                ),
            )
        )
        checks.append({
            "name": "modular_remainder_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "modular_remainder_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Second verified proof: if 0 <= n < 101 and 123456 ≡ n (mod 101), then n = 34.
    try:
        n = Int("n")
        thm2 = kd.prove(
            ForAll(
                [n],
                Implies(
                    And(n >= 0, n < 101, (123456 - n) % 101 == 0),
                    n == 34,
                ),
            )
        )
        checks.append({
            "name": "uniqueness_of_remainder_34",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "uniqueness_of_remainder_34",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check.
    try:
        remainder = 123456 % 101
        passed = (remainder == 34)
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_remainder_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"123456 % 101 = {remainder}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_remainder_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)