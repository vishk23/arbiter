from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Verified proof: formalize the arithmetic-series derivation in Z3.
    a = Int("a")
    theorem = ForAll(
        [a],
        Implies(
            And(5 * a + 20 == 60),
            a == 8,
        ),
    )
    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "solve_linear_equation_for_smallest_even_integer",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {proof}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "solve_linear_equation_for_smallest_even_integer",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Verified proof: the sum of the first 8 odd positive integers is 64.
    # Encode as a concrete arithmetic fact in Z3.
    try:
        sum_first_8_odds = 1 + 3 + 5 + 7 + 9 + 11 + 13 + 15
        proof2 = kd.prove(sum_first_8_odds == 64)
        checks.append(
            {
                "name": "sum_first_8_odd_numbers_equals_64",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {proof2}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "sum_first_8_odd_numbers_equals_64",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check.
    a_val = 8
    even_sum = sum(a_val + 2 * i for i in range(5))
    odd_sum = sum(2 * i + 1 for i in range(8))
    numerical_passed = (even_sum == odd_sum - 4) and (a_val == 8)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For a=8, even_sum={even_sum}, odd_sum={odd_sum}, and even_sum == odd_sum - 4 is {even_sum == odd_sum - 4}.",
        }
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)