import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Use the equation
    #   (p-1)(q-1)(r-1) | pqr - 1
    # and write
    #   pqr - 1 = k (p-1)(q-1)(r-1)
    # for some integer k.
    # Expanding and simplifying gives
    #   (k-1)pqr - k(pq+pr+qr) + k(p+q+r) + (k-1) = 0.
    # Since p<q<r and p>1, we can use standard bounding to show k is 1 or 2.
    # Then a finite case split determines the only solutions.

    p, q, r, k = Ints('p q r k')

    # Basic constraints.
    constraints = [p > 1, p < q, q < r, k >= 1]
    divisibility = Exists(k, p*q*r - 1 == k * (p - 1) * (q - 1) * (r - 1))

    # Candidate solutions.
    sol1 = And(p == 2, q == 4, r == 8)
    sol2 = And(p == 3, q == 5, r == 15)
    target = Or(sol1, sol2)

    # Check 1: the claimed solutions really satisfy the divisibility.
    try:
        ok1 = kd.prove(Implies(sol1, (p*q*r - 1) % ((p - 1)*(q - 1)*(r - 1)) == 0))
        ok2 = kd.prove(Implies(sol2, (p*q*r - 1) % ((p - 1)*(q - 1)*(r - 1)) == 0))
        checks.append({
            "name": "candidate_solutions_check",
            "passed": True,
            "backend": "z3",
            "proof_type": "theorem",
            "details": "Both candidate triples satisfy the divisibility condition."
        })
    except Exception as e:
        checks.append({
            "name": "candidate_solutions_check",
            "passed": False,
            "backend": "z3",
            "proof_type": "theorem",
            "details": f"Could not verify candidate solutions: {e!r}"
        })

    # Check 2: show there is no extra solution beyond the two candidates.
    # We ask Z3 for a counterexample to the negation of the conclusion.
    try:
        ce = Exists([p, q, r], And(p > 1, p < q, q < r,
                                  (p*q*r - 1) % ((p - 1)*(q - 1)*(r - 1)) == 0,
                                  Not(target)))
        kd.prove(Not(ce))
        checks.append({
            "name": "uniqueness_of_solutions",
            "passed": True,
            "backend": "z3",
            "proof_type": "theorem",
            "details": "No counterexample exists; only the two stated triples occur."
        })
    except Exception as e:
        checks.append({
            "name": "uniqueness_of_solutions",
            "passed": False,
            "backend": "z3",
            "proof_type": "theorem",
            "details": f"Uniqueness proof failed: {e!r}"
        })

    return checks