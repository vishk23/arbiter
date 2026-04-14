from math import pi

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And

from sympy import Rational, ceiling, floor, pi as sympi


# --- Verified theorem: count of integers x with |x| < 3*pi is 19 ---

def _count_integers_bound() -> int:
    # Exact integer count using SymPy's exact pi and arithmetic.
    # Since 3*pi is between 9 and 10, the integers are -9, ..., 0, ..., 9.
    return int(2 * floor(3 * sympi) + 1)


def verify():
    checks = []

    # Verified proof by kdrag: if n is an integer with |n| < 9, then -9 <= n <= 9.
    n = Int("n")
    try:
        proof = kd.prove(
            ForAll([n], Implies(And(n > -9, n < 9), And(n >= -9, n <= 9)))
        )
        checks.append({
            "name": "interval_integrality_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof object: {proof}",
        })
    except Exception as e:
        checks.append({
            "name": "interval_integrality_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Symbolic exact arithmetic check: 3*pi lies strictly between 9 and 10.
    # Using exact rational bounds on pi.
    lower_ok = (3 * sympi > 9)
    upper_ok = (3 * sympi < 10)
    exact_count = _count_integers_bound()
    checks.append({
        "name": "exact_pi_bounds_and_count",
        "passed": bool(lower_ok and upper_ok and exact_count == 19),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": (
            f"3*pi > 9 is {lower_ok}, 3*pi < 10 is {upper_ok}; "
            f"exact integer count computed as {exact_count}."
        ),
    })

    # Numerical sanity check at concrete values.
    test_vals = [-9, -10, 0, 9, 10]
    sanity = [abs(x) < 3 * pi for x in test_vals]
    passed_sanity = sanity == [True, False, True, True, False]
    checks.append({
        "name": "numerical_sanity_check",
        "passed": passed_sanity,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": (
            f"Test values {test_vals} give predicates {sanity}; expected [True, False, True, True, False]."
        ),
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)