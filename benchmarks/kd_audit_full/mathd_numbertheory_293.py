from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: the alternating sum criterion reduces the divisibility condition
    # to a digit equation with a unique solution.
    try:
        A = Int("A")
        # For a digit A, if 20A7 is divisible by 11, then its alternating sum must be a multiple of 11:
        # 2 - 0 + A - 7 = A - 5.
        # Since A is a digit, A-5 is in [-5,4], so the only multiple of 11 it can equal is 0.
        thm = kd.prove(
            ForAll(
                [A],
                Implies(
                    And(A >= 0, A <= 9, (2000 + 10 * A + 7) % 11 == 0),
                    A == 5,
                ),
            )
        )
        checks.append(
            {
                "name": "divisibility_by_11_for_20A7_implies_A_equals_5",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kd.prove(): {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "divisibility_by_11_for_20A7_implies_A_equals_5",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the claimed digit.
    n = 2000 + 10 * 5 + 7
    passed_num = (n % 11 == 0)
    checks.append(
        {
            "name": "numerical_check_2057_divisible_by_11",
            "passed": passed_num,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"2057 % 11 = {n % 11}; alternating sum 2-0+5-7 = {2 - 0 + 5 - 7}.",
        }
    )
    if not passed_num:
        proved = False

    # Check that all other digits fail numerically.
    failures = []
    for d in range(10):
        if d != 5 and (2000 + 10 * d + 7) % 11 == 0:
            failures.append(d)
    passed_unique = (len(failures) == 0)
    checks.append(
        {
            "name": "uniqueness_of_digit",
            "passed": passed_unique,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "No digit other than 5 makes 20A7 divisible by 11." if passed_unique else f"Unexpected digits: {failures}",
        }
    )
    if not passed_unique:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)