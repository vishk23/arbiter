from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def ones_digit(n: int) -> int:
    return abs(n) % 10


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved_all = True

    # Verified proof: any integer ending in 5 stays ending in 5 after multiplying by an integer.
    try:
        a = Int("a")
        thm = kd.prove(ForAll([a], Implies(a % 2 == 1, (5 * a) % 10 == 5)))
        checks.append(
            {
                "name": "odd_multiplier_times_five_has_ones_digit_five",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved by kdrag: {thm}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "odd_multiplier_times_five_has_ones_digit_five",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Another verified proof: the concrete product is congruent to 5 mod 10.
    try:
        p = 1 * 3 * 5 * 7 * 9 * 11 * 13
        # p is a concrete integer; kdrag can prove its modulo statement directly.
        thm2 = kd.prove((p % 10) == 5)
        checks.append(
            {
                "name": "concrete_product_mod_10_is_5",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Concrete arithmetic verified by kdrag: {thm2}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "concrete_product_mod_10_is_5",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag concrete proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check.
    product = 1 * 3 * 5 * 7 * 9 * 11 * 13
    num_pass = ones_digit(product) == 5
    checks.append(
        {
            "name": "numerical_sanity_check_product_ones_digit",
            "passed": num_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Product={product}, ones digit={ones_digit(product)}.",
        }
    )
    if not num_pass:
        proved_all = False

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)