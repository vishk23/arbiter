import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Main verified proof: gcd(21n+4, 14n+3) = 1 for all natural numbers n.
    n = Int("n")
    a = 21 * n + 4
    b = 14 * n + 3
    gcd_is_one = ForAll(
        [n],
        Implies(
            n >= 0,
            And(
                (a % b) == a - b * (a / b),
                # The actual proof target is coprimality; Z3 can prove the stronger
                # divisibility characterization below via linear arithmetic.
                Exists(
                    [Int("d")],
                    Implies(
                        And(Int("d") > 0, a % Int("d") == 0, b % Int("d") == 0),
                        Int("d") == 1,
                    ),
                ),
            ),
        ),
    )

    try:
        # Directly prove the gcd characterization from the Euclidean-algorithm fact:
        # any common divisor of a and b also divides (a-b)=7n+1, and then
        # divides b-2(a-b)=1, hence must be 1.
        d = Int("d")
        thm = kd.prove(
            ForAll(
                [n, d],
                Implies(
                    And(n >= 0, d > 0, a % d == 0, b % d == 0),
                    d == 1,
                ),
            )
        )
        checks.append(
            {
                "name": "euclidean_algorithm_coprime",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified kd.prove certificate: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "euclidean_algorithm_coprime",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove coprimality in kdrag: {e}",
            }
        )

    # Numerical sanity check at a concrete value.
    try:
        n0 = 5
        num = 21 * n0 + 4
        den = 14 * n0 + 3
        import math

        g = math.gcd(num, den)
        passed = (g == 1) and (num == 109) and (den == 73)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"n={n0}: numerator={num}, denominator={den}, gcd={g}",
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
                "details": f"Numerical check failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)