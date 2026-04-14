from itertools import combinations

import kdrag as kd
from kdrag.smt import Int, IntVal, And, Or, Not, Implies, ForAll, Exists

from sympy import Integer


def verify():
    checks = []
    proved = True

    # Prime choices between 4 and 18
    primes = [5, 7, 11, 13, 17]
    target = 119
    candidates = [22, 60, 119, 180, 231]

    # Check 1: verify the exact result is attainable by a prime pair (7,17)
    try:
        p, q = Int("p"), Int("q")
        thm1 = kd.prove(
            Exists([p, q], And(p == 7, q == 17, p != q, p > 4, p < 18, q > 4, q < 18))
        )
        # The above only states the witness primes exist; separately compute the expression.
        expr_val = 7 * 17 - (7 + 17)
        passed = isinstance(thm1, kd.Proof) and expr_val == target
        checks.append({
            "name": "attainable_value_119",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Witness primes (7,17) are within the range and distinct; computed value is {expr_val}.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "attainable_value_119",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })
        proved = False

    # Check 2: prove parity restriction over all allowed prime pairs using a finite exhaustive argument.
    # Since the possible primes are explicitly finite, we can verify by enumeration and also
    # provide a certified arithmetic fact for the parity of any such product-sum.
    try:
        parity_ok = True
        for a, b in combinations(primes, 2):
            v = a * b - (a + b)
            if v % 2 != 1:
                parity_ok = False
                break
        # A tiny certified arithmetic check for one generic pair form is not needed; the exhaustive
        # finite check itself is the verification here.
        passed = parity_ok
        checks.append({
            "name": "parity_of_all_candidates_is_odd",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Exhaustive check over all distinct prime pairs in {5,7,11,13,17} confirms the value is always odd.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "parity_of_all_candidates_is_odd",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Exhaustive parity check failed: {e}",
        })
        proved = False

    # Check 3: exhaustive candidate elimination and identification of 119.
    try:
        vals = sorted({a * b - (a + b) for a, b in combinations(primes, 2)})
        passed = (target in vals) and all(c not in vals for c in [22, 60, 180, 231]) and (119 in vals)
        checks.append({
            "name": "candidate_elimination_and_unique_choice",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Possible values are {vals}; among the options, only 119 occurs.",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "candidate_elimination_and_unique_choice",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Candidate elimination failed: {e}",
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())