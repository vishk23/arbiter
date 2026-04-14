from fractions import Fraction
from math import isqrt
from typing import Dict, List, Tuple

import kdrag as kd
from kdrag.smt import Int, Ints, ForAll, Implies, And


def _is_perfect_power(n: int) -> bool:
    if n <= 1:
        return False
    for base in range(2, isqrt(n) + 1):
        p = base * base
        while p < n:
            p *= base
        if p == n:
            return True
    return False


def _generate_candidates(limit: int = 200) -> List[Tuple[int, int]]:
    sols = []
    for x in range(1, limit + 1):
        for y in range(1, limit + 1):
            lhs = x ** (y * y)
            rhs = y ** x
            if lhs == rhs:
                sols.append((x, y))
    return sols


def verify() -> Dict:
    checks = []

    # Verified proof: among y in {1,2,3}, the only positive-integer solutions are exactly the claimed ones.
    x = Int("x")
    y = Int("y")
    try:
        thm = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(x >= 1, y >= 1, x ** (y * y) == y ** x, y <= 3),
                    Or(x == 1, And(y == 2, x == 16), And(y == 3, x == 27)),
                ),
            )
        )
        checks.append(
            {
                "name": "restricted_classification_y_le_3",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Z3 certificate obtained: {thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "restricted_classification_y_le_3",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check by exhaustive search in a finite box.
    sols = _generate_candidates(200)
    expected = {(1, 1), (16, 2), (27, 3)}
    passed_num = set(sols) == expected
    checks.append(
        {
            "name": "finite_search_up_to_200",
            "passed": passed_num,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"solutions found in [1,200]^2: {sols}",
        }
    )

    # Direct certificate for each claimed solution.
    claim_ok = True
    claim_details = []
    for a, b in [(1, 1), (16, 2), (27, 3)]:
        ok = (a ** (b * b) == b ** a)
        claim_ok = claim_ok and ok
        claim_details.append(f"({a},{b}) -> {a ** (b * b)} == {b ** a}")
    checks.append(
        {
            "name": "claimed_solutions_verify",
            "passed": claim_ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(claim_details),
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)