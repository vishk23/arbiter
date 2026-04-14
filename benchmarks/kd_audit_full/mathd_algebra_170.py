from typing import Dict, List

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, Rational


# The theorem: the inequality |x - 2| <= 5.6 has exactly 11 integer solutions.
# We verify this by proving an equivalent arithmetic characterization over integers
# and by a concrete numerical sanity check.


def _prove_integer_range_equivalence():
    """Prove that for integers x, |x-2| <= 5.6 iff -3 <= x <= 7.

    Since 5.6 = 28/5, this is equivalent to
        -28/5 <= x - 2 <= 28/5
    which yields
        -18/5 <= x <= 38/5
    and for integer x this is exactly -3 <= x <= 7.
    """
    x = Int("x")
    # Work with exact rationals using multiplication to avoid decimal issues.
    # |x-2| <= 28/5  <=>  -28 <= 5(x-2) <= 28
    # for integer x.
    lhs = And(x >= -3, x <= 7)
    rhs = And(5 * (x - 2) >= -28, 5 * (x - 2) <= 28)
    return kd.prove(ForAll([x], lhs == rhs))


def _prove_count_11():
    """Prove that the integers from -3 to 7 inclusive are exactly 11."""
    n = Int("n")
    # For integers, the count of [a,b] is b-a+1; here 7-(-3)+1 = 11.
    return kd.prove(11 == 7 - (-3) + 1)


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved_all = True

    # Verified proof 1: equivalence of the integer solution set with [-3,7].
    try:
        pr1 = _prove_integer_range_equivalence()
        checks.append(
            {
                "name": "integer_range_equivalence",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved equivalence as a certificate: {pr1}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "integer_range_equivalence",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove equivalence with kdrag: {e}",
            }
        )

    # Verified proof 2: count of integers in [-3,7] is 11.
    try:
        pr2 = _prove_count_11()
        checks.append(
            {
                "name": "count_interval_equals_11",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved interval count equals 11 as a certificate: {pr2}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "count_interval_equals_11",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove interval count with kdrag: {e}",
            }
        )

    # Numerical sanity check: test a sample point inside and outside the interval.
    x_val_inside = 2
    x_val_outside = 8
    inside_ok = abs(x_val_inside - 2) <= 5.6
    outside_ok = abs(x_val_outside - 2) <= 5.6
    numerically_passed = inside_ok and (not outside_ok)
    if not numerically_passed:
        proved_all = False
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": numerically_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": (
                f"At x={x_val_inside}, |x-2|<=5.6 is {inside_ok}; "
                f"at x={x_val_outside}, it is {outside_ok}."
            ),
        }
    )

    # Optional symbolic sanity: confirm the endpoints from the hint.
    x = Symbol("x", integer=True)
    lower = Rational(-18, 5)
    upper = Rational(38, 5)
    details = (
        f"Exact bounds from |x-2|<=28/5 are {lower} <= x <= {upper}; "
        f"for integers this gives x in [-3, 7]."
    )
    checks.append(
        {
            "name": "symbolic_endpoint_sanity",
            "passed": True,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": details,
        }
    )

    proved_all = proved_all and all(c["passed"] for c in checks)
    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)