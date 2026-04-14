from itertools import product

import kdrag as kd
from kdrag.smt import Ints, And, Or, Implies, ForAll, IntVal


def objective(a, m, c):
    return a * m * c + a * m + m * c + a * c


def verify():
    checks = []

    # Verified proof: no integer triple summing to 12 can beat the claimed maximum 112.
    # We encode the theorem directly over integers and ask Z3/kdrag to prove it.
    A, M, C = Ints("A M C")
    theorem = ForAll(
        [A, M, C],
        Implies(
            And(A >= 0, M >= 0, C >= 0, A + M + C == 12),
            objective(A, M, C) <= 112,
        ),
    )
    try:
        prf = kd.prove(theorem)
        checks.append(
            {
                "name": "global_upper_bound_112",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {prf}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "global_upper_bound_112",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Verified proof that the candidate assignment (4,4,4) attains 112.
    try:
        prf2 = kd.prove(objective(4, 4, 4) == 112)
        checks.append(
            {
                "name": "candidate_value_444",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {prf2}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "candidate_value_444",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete point.
    num_val = objective(4, 4, 4)
    checks.append(
        {
            "name": "numerical_sanity_444",
            "passed": num_val == 112,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"objective(4,4,4) = {num_val}",
        }
    )

    # Exhaustive finite search over all nonnegative integer triples summing to 12.
    # This is a computational check, not the primary proof.
    best = None
    argmax = None
    for a in range(13):
        for m in range(13 - a):
            c = 12 - a - m
            val = objective(a, m, c)
            if best is None or val > best:
                best = val
                argmax = (a, m, c)
    checks.append(
        {
            "name": "finite_search_maximum",
            "passed": best == 112 and argmax == (4, 4, 4),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"max value {best} attained at {argmax}",
        }
    )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)