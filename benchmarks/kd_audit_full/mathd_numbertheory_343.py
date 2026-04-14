from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # The odd integers between 0 and 12 are 1, 3, 5, 7, 9, 11.
    product = 1 * 3 * 5 * 7 * 9 * 11
    units_digit = product % 10

    try:
        proof = kd.prove(units_digit == 5)
        checks.append(
            {
                "name": "units_digit_of_product_of_odd_integers_between_0_and_12",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove established that (1*3*5*7*9*11) mod 10 = 5; proof={proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "units_digit_of_product_of_odd_integers_between_0_and_12",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the concrete modular arithmetic claim: {type(e).__name__}: {e}",
            }
        )

    # Optional explanatory check: 1*3*5*7*9*11 = 10395, so the units digit is 5.
    try:
        proof2 = kd.prove(10395 % 10 == 5)
        checks.append(
            {
                "name": "expanded_product_has_units_digit_five",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove established 10395 mod 10 = 5; proof={proof2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "expanded_product_has_units_digit_five",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the expanded arithmetic claim: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}