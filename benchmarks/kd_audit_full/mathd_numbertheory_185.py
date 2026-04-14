from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: if n has remainder 3 mod 5, then 2n has remainder 1 mod 5.
    try:
        n = Int("n")
        theorem = ForAll(
            [n],
            Implies(
                And(n >= 0, n % 5 == 3),
                (2 * n) % 5 == 1,
            ),
        )
        proof = kd.prove(theorem)
        checks.append(
            {
                "name": "mod5_double_remainder_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded with proof: {proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "mod5_double_remainder_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete value n = 8 (8 % 5 = 3, 16 % 5 = 1).
    try:
        n_val = 8
        lhs = n_val % 5
        rhs = (2 * n_val) % 5
        passed = (lhs == 3) and (rhs == 1)
        checks.append(
            {
                "name": "numerical_sanity_example",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"n={n_val}, n%5={lhs}, (2n)%5={rhs}",
            }
        )
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_example",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)