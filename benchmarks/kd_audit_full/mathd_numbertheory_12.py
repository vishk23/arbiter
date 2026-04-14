from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import *


# The theorem: exactly four integers between 15 and 85 are divisible by 20.
# We formalize and prove the key counting facts with Z3-backed verification.


def _prove_divisibility_characterization():
    """Prove that among integers n with 15 < n < 85, divisibility by 20
    is equivalent to n being one of 20, 40, 60, 80.
    """
    n = Int("n")
    thm = kd.prove(
        ForAll(
            [n],
            Implies(
                And(n > 15, n < 85, n % 20 == 0),
                Or(n == 20, n == 40, n == 60, n == 80),
            ),
        )
    )
    return thm


def _prove_each_multiple_in_interval():
    """Prove that 20, 40, 60, 80 are indeed strictly between 15 and 85
    and divisible by 20.
    """
    x = Int("x")
    thm = kd.prove(
        And(
            20 > 15,
            20 < 85,
            20 % 20 == 0,
            40 > 15,
            40 < 85,
            40 % 20 == 0,
            60 > 15,
            60 < 85,
            60 % 20 == 0,
            80 > 15,
            80 < 85,
            80 % 20 == 0,
        )
    )
    return thm


def _prove_count_is_four():
    """Prove that there are exactly four integers in the open interval (15, 85)
    divisible by 20, by showing any such integer must be one of four and that
    all four occur.
    """
    n = Int("n")
    # Any integer divisible by 20 in the interval must be one of the four listed.
    cover = kd.prove(
        ForAll(
            [n],
            Implies(
                And(n > 15, n < 85, n % 20 == 0),
                Or(n == 20, n == 40, n == 60, n == 80),
            ),
        )
    )
    # The four candidates are all distinct.
    distinct = kd.prove(And(20 != 40, 20 != 60, 20 != 80, 40 != 60, 40 != 80, 60 != 80))
    return cover, distinct


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof check 1: characterization of all divisible integers in the interval.
    try:
        thm1 = _prove_divisibility_characterization()
        checks.append(
            {
                "name": "characterize_multiples_of_20_between_15_and_85",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm1),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "characterize_multiples_of_20_between_15_and_85",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {e}",
            }
        )

    # Verified proof check 2: the candidates are valid and distinct.
    try:
        thm2 = _prove_each_multiple_in_interval()
        checks.append(
            {
                "name": "verify_four_multiples_are_in_interval",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm2),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "verify_four_multiples_are_in_interval",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {e}",
            }
        )

    try:
        cover, distinct = _prove_count_is_four()
        checks.append(
            {
                "name": "distinctness_of_candidates",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"{cover}; {distinct}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "distinctness_of_candidates",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {e}",
            }
        )

    # Numerical sanity check: enumerate the integers in a concrete computation.
    try:
        vals = [n for n in range(16, 85) if n % 20 == 0]
        passed = vals == [20, 40, 60, 80]
        checks.append(
            {
                "name": "numerical_enumeration_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Multiples in (15,85): {vals}",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_enumeration_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )

    # Final conclusion as a derived statement: there are exactly four such integers.
    # We keep this as a logical conclusion in the returned result.
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)