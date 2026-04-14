from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, And, ForAll, Implies


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: A verified proof that any digit n making 374n divisible by 18 must be 4.
    # We encode the digit as an integer n with 0 <= n <= 9.
    n = Int("n")
    theorem = ForAll(
        [n],
        Implies(
            And(n >= 0, n <= 9, (3740 + n) % 18 == 0),
            n == 4,
        ),
    )
    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "divisible_by_18_implies_digit_4",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified with kd.prove: {proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "divisible_by_18_implies_digit_4",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Directly verify the candidate digit 4 works.
    try:
        proof2 = kd.prove((3740 + 4) % 18 == 0)
        checks.append(
            {
                "name": "candidate_digit_4_divisible_by_18",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified with kd.prove: {proof2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "candidate_digit_4_divisible_by_18",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Numerical sanity check by brute force over all digits.
    sols = [d for d in range(10) if (3740 + d) % 18 == 0]
    passed3 = sols == [4]
    checks.append(
        {
            "name": "bruteforce_digit_search",
            "passed": passed3,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Digits d in [0,9] with (3740+d) % 18 == 0: {sols}",
        }
    )
    if not passed3:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)