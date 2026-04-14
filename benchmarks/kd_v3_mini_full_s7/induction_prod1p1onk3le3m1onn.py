from fractions import Fraction
from typing import Dict, List

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []

    # Verified proof check: induction step arithmetic inequality encoded in Z3.
    # We prove the algebraic core used in the inductive step:
    # for n >= 1, n^2 - n + 2 >= 0.
    n = Int("n")
    try:
        thm = kd.prove(ForAll([n], Implies(n >= 1, n*n - n + 2 >= 0)))
        checks.append({
            "name": "induction_step_arithmetic_core",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by kdrag: {thm}",
        })
    except Exception as e:
        checks.append({
            "name": "induction_step_arithmetic_core",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at concrete values.
    def prod_value(N: int) -> Fraction:
        p = Fraction(1, 1)
        for k in range(1, N + 1):
            p *= Fraction(k**3 + 1, k**3)
        return p

    sanity_points = [1, 2, 3, 5, 10]
    ok = True
    details = []
    for N in sanity_points:
        lhs = prod_value(N)
        rhs = Fraction(3, 1) - Fraction(1, N)
        passed = lhs <= rhs
        ok = ok and passed
        details.append(f"n={N}: lhs={lhs}, rhs={rhs}, passed={passed}")
    checks.append({
        "name": "numerical_sanity_samples",
        "passed": ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "; ".join(details),
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)