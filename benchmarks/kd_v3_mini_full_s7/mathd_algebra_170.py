import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []

    # Verified proof: the integer interval [-3, 7] contains exactly 11 integers.
    n = Int("n")
    thm = None
    try:
        thm = kd.prove(
            ForAll(
                [n],
                Implies(
                    And(n >= -3, n <= 7),
                    Or(
                        n == -3,
                        n == -2,
                        n == -1,
                        n == 0,
                        n == 1,
                        n == 2,
                        n == 3,
                        n == 4,
                        n == 5,
                        n == 6,
                        n == 7,
                    ),
                ),
            )
        )
        checks.append(
            {
                "name": "interval_membership_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kd.prove verified the interval [-3, 7] is exactly covered by the 11 integers -3 through 7.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "interval_membership_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Derived counting fact: 7 - (-3) + 1 = 11.
    try:
        count_proof = kd.prove(7 - (-3) + 1 == 11)
        checks.append(
            {
                "name": "count_formula_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kd.prove verified the arithmetic count 7 - (-3) + 1 = 11.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "count_formula_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag arithmetic proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: enumerate integers in the interval.
    ints = [k for k in range(-3, 8)]
    numerical_ok = (len(ints) == 11 and ints[0] == -3 and ints[-1] == 7)
    checks.append(
        {
            "name": "numerical_interval_enumeration",
            "passed": numerical_ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Enumerated integers from -3 to 7 inclusive: {ints}; count={len(ints)}.",
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)