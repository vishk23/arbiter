import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Certified proof: if n is a multiple of 3, then
    # (n+4) + (n+6) + (n+8) = 3n + 18 = 3(n+6), which is divisible by 9
    # exactly when n is divisible by 3.
    n = Int("n")
    try:
        thm = kd.prove(
            ForAll(
                [n],
                Implies(
                    n % 3 == 0,
                    (((n + 4) + (n + 6) + (n + 8)) % 9) == 0,
                ),
            )
        )
        checks.append(
            {
                "name": "divisibility_remainder_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned a Proof object: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "divisibility_remainder_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to certify the modular claim with kdrag: {e}",
            }
        )

    # Additional numerical sanity check on a concrete multiple of 3.
    try:
        n0 = 12
        expr0 = (n0 + 4) + (n0 + 6) + (n0 + 8)
        passed = (expr0 % 9 == 0) and (expr0 == 3 * n0 + 18)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For n={n0}, sum={expr0}, sum mod 9={expr0 % 9}.",
            }
        )
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())