import kdrag as kd
from kdrag.smt import *


def _proof_count_multiples() -> kd.Proof:
    # The theorem is that there are exactly 4 integers n with 15 <= n <= 85 and 20 | n.
    # Encode the concrete divisibility cases by checking the only possible multiples.
    n = Int("n")
    thm = ForAll(
        [n],
        Implies(
            And(n >= 15, n <= 85, n % 20 == 0),
            Or(n == 20, n == 40, n == 60, n == 80),
        ),
    )
    return kd.prove(thm)


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof certificate: every integer in the interval divisible by 20
    # must be one of 20, 40, 60, 80.
    try:
        proof = _proof_count_multiples()
        checks.append(
            {
                "name": "interval_divisible_numbers_are_only_four_multiples",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified theorem proved: {proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "interval_divisible_numbers_are_only_four_multiples",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: enumerate the concrete multiples.
    multiples = [n for n in range(16, 85) if n % 20 == 0]
    num_ok = (len(multiples) == 4 and multiples == [20, 40, 60, 80])
    checks.append(
        {
            "name": "numerical_enumeration_of_multiples",
            "passed": num_ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Enumerated multiples in [16,84]: {multiples}; count={len(multiples)}.",
        }
    )
    proved = proved and num_ok

    # A second verified proof: show any candidate multiple in the interval is one of the four.
    # This is the exact finite characterization needed for the count.
    try:
        n = Int("n")
        candidate_set = kd.prove(
            ForAll(
                [n],
                Implies(
                    And(n >= 15, n <= 85, n % 20 == 0),
                    Or(n == 20, n == 40, n == 60, n == 80),
                ),
            )
        )
        checks.append(
            {
                "name": "finite_characterization_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified finite characterization: {candidate_set}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "finite_characterization_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Final conclusion: there are exactly 4 such integers.
    checks.append(
        {
            "name": "final_answer",
            "passed": proved,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "There are exactly four integers divisible by 20 between 15 and 85: 20, 40, 60, 80.",
        }
    )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())