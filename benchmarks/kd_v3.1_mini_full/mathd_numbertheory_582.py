import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []

    # Verified proof: if n is a multiple of 3, then (n+4)+(n+6)+(n+8) is divisible by 9.
    n, k = Ints("n k")
    expr = (n + 4) + (n + 6) + (n + 8)

    try:
        # Use the witness n = 3k for multiples of 3.
        thm = kd.prove(
            ForAll([k], ((3 * k + 4) + (3 * k + 6) + (3 * k + 8)) % 9 == 0)
        )
        checks.append(
            {
                "name": "divisible_by_9_when_n_is_multiple_of_3",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified theorem: {thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "divisible_by_9_when_n_is_multiple_of_3",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete multiple of 3.
    n_val = 12
    remainder = ((n_val + 4) + (n_val + 6) + (n_val + 8)) % 9
    checks.append(
        {
            "name": "numerical_sanity_check_n_12",
            "passed": remainder == 0,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For n={n_val}, remainder is {remainder}.",
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)