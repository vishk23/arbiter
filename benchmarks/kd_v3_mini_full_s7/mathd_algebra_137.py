from fractions import Fraction

import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: Verified symbolic proof in kdrag/Z3.
    # Let x be last year's enrollment. A 4% increase means:
    #   x + 0.04*x = 598
    # Using exact rationals, 0.04 = 1/25, so the equation is:
    #   x + x/25 = 598
    # which implies (26/25)x = 598, hence x = 575.
    x = Real("x")
    thm = None
    try:
        thm = kd.prove(
            ForAll(
                [x],
                Implies(
                    x + x / 25 == 598,
                    x == 575,
                ),
            )
        )
        checks.append(
            {
                "name": "kdrag_prove_last_year_enrollment",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved implication from x + x/25 = 598 to x = 575. Proof: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "kdrag_prove_last_year_enrollment",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the enrollment equation in kdrag: {e}",
            }
        )

    # Check 2: Numerical sanity check with exact arithmetic.
    # 575 increased by 4% is 598.
    try:
        last_year = Fraction(575, 1)
        new_enrollment = last_year * Fraction(26, 25)
        passed_num = (new_enrollment == 598)
        checks.append(
            {
                "name": "numerical_sanity_575_times_1p04_is_598",
                "passed": passed_num,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed 575 * 26/25 = {new_enrollment}; expected 598.",
            }
        )
        proved = proved and passed_num
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_575_times_1p04_is_598",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {e}",
            }
        )

    # Check 3: Exact arithmetic verification of the backward computation.
    # 598 / 1.04 = 575, using exact rational arithmetic.
    try:
        exact = Fraction(598, 1) / Fraction(26, 25)
        passed_exact = (exact == 575)
        checks.append(
            {
                "name": "exact_backward_division_598_over_1p04_is_575",
                "passed": passed_exact,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed 598 / (26/25) = {exact}; expected 575.",
            }
        )
        proved = proved and passed_exact
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "exact_backward_division_598_over_1p04_is_575",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Exact backward division check failed: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)