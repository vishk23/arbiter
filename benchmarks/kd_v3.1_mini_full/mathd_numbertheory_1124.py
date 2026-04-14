import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Check 1: Formal proof that the only digit n with 374n divisible by 18 is 4.
    # We encode the digit as an integer n in [0, 9] and prove the exact equivalence.
    n = Int("n")
    try:
        proof = kd.prove(
            ForAll(
                [n],
                Implies(
                    And(n >= 0, n <= 9, (3740 + n) % 18 == 0),
                    n == 4,
                ),
            )
        )
        checks.append(
            {
                "name": "divisibility_implies_n_is_4",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified by Z3-backed proof: {proof}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "divisibility_implies_n_is_4",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Direct certificate that 3744 is divisible by 18.
    try:
        proof2 = kd.prove((3740 + 4) % 18 == 0)
        checks.append(
            {
                "name": "3744_divisible_by_18",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified by Z3-backed proof: {proof2}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "3744_divisible_by_18",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check on concrete candidates.
    candidates = [(d, (3740 + d) % 18) for d in range(10)]
    passed_num = any(d == 4 and r == 0 for d, r in candidates) and all(
        (r != 0) or (d == 4) for d, r in candidates
    )
    checks.append(
        {
            "name": "numerical_sanity_check_candidates",
            "passed": passed_num,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Remainders for 3740+d mod 18 over d=0..9: {candidates}",
        }
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)