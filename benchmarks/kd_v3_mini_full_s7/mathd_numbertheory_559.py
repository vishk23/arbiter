import kdrag as kd
from kdrag.smt import *


def _smallest_candidate_search(limit=200):
    candidates = []
    for n in range(1, limit + 1):
        if n % 3 == 2 and n % 10 == 4:
            candidates.append(n)
    return candidates


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof that any positive integer with units digit 4 and congruent to 2 mod 3
    # must be at least 14, and 14 itself satisfies the conditions.
    n = Int("n")
    try:
        thm = kd.prove(
            ForAll(
                [n],
                Implies(
                    And(n > 0, n % 3 == 2, n % 10 == 4),
                    n >= 14,
                ),
            )
        )
        checks.append(
            {
                "name": "kdrag_minimality_of_14",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "kdrag_minimality_of_14",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Verified proof that 14 satisfies the congruence and digit conditions.
    try:
        thm2 = kd.prove(And(14 > 0, 14 % 3 == 2, 14 % 10 == 4))
        checks.append(
            {
                "name": "kdrag_14_satisfies_conditions",
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
                "name": "kdrag_14_satisfies_conditions",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Numerical sanity check by brute-force search.
    cand = _smallest_candidate_search(100)
    passed3 = (len(cand) > 0 and cand[0] == 14)
    if not passed3:
        proved = False
    checks.append(
        {
            "name": "numerical_search_smallest_candidate",
            "passed": passed3,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Candidates up to 100: {cand[:10]}... smallest={cand[0] if cand else None}",
        }
    )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())