from fractions import Fraction

import kdrag as kd
from kdrag.smt import *

from sympy import Rational


def verify():
    checks = []
    proved = True

    # Verified proof: the floor values for N = 1/3 at the required scales.
    try:
        n = Real("n")
        thm = kd.prove(
            ForAll(
                [n],
                Implies(
                    n == Rational(1, 3),
                    And(
                        ToInt(10 * n) == 3,
                        ToInt(100 * n) == 33,
                        ToInt(1000 * n) == 333,
                        ToInt(10000 * n) == 3333,
                    ),
                ),
            )
        )
        checks.append(
            {
                "name": "floor_values_for_n_equals_one_third",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "floor_values_for_n_equals_one_third",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Verified proof of the arithmetic sum.
    try:
        s = 3 + 33 + 333 + 3333
        sum_thm = kd.prove(s == 3702)
        checks.append(
            {
                "name": "sum_equals_3702",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {sum_thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sum_equals_3702",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at concrete values.
    try:
        N = Fraction(1, 3)
        val = sum(int((10**k * N) // 1) for k in [1, 2, 3, 4])
        passed = (val == 3702)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed floor-sum with Fraction(1, 3): {val}",
            }
        )
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
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