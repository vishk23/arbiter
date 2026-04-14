from fractions import Fraction
from math import gcd


def compute_f_via_reduction(a: int, b: int) -> Fraction:
    """Compute f(a,b) using the functional equation and symmetry.

    We repeatedly replace the larger argument by the difference with the smaller
    argument, using
        f(x, x+y) = (x+y)/y * f(x, y)
    which follows from (x+y)f(x,y)=y f(x,x+y).

    By symmetry, f(x,y)=f(y,x), so the reduction can continue with ordered pairs.
    """
    x, y = a, b
    value = Fraction(1, 1)
    while True:
        if x == y:
            return value * x
        if x > y:
            # Use symmetry to swap to keep x < y for the reduction step.
            x, y = y, x
        # Now y > x, and by the FE: (x+y) f(x,y) = y f(x,x+y)
        # so f(x, x+y) = (x+y)/y * f(x,y).
        # Equivalently, f(x, y) = y/(y-x) * f(x, y-x).
        value *= Fraction(y, y - x)
        y -= x


def verify() -> dict:
    checks = []

    # Proof check: compute f(14,52) by the exact reduction implied by the axioms.
    proof_value = compute_f_via_reduction(14, 52)
    proof_passed = (proof_value == 364)
    checks.append({
        "name": "proof_f_14_52_equals_364",
        "passed": proof_passed,
        "check_type": "proof",
        "backend": "numerical",
        "details": f"Computed exact value via functional-equation reduction: f(14,52) = {proof_value}",
    })

    # Sanity check: ensure the reduction is non-trivial and consistent on a smaller example.
    sanity_value = compute_f_via_reduction(2, 4)
    sanity_passed = (sanity_value == 4)
    checks.append({
        "name": "sanity_reduction_on_2_4",
        "passed": sanity_passed,
        "check_type": "sanity",
        "backend": "numerical",
        "details": f"Non-trivial reduction example: f(2,4) = {sanity_value}",
    })

    # Numerical check: explicitly follow the hinted chain for 14 and 52.
    chain = [
        Fraction(52, 38),
        Fraction(38, 24),
        Fraction(24, 10),
        Fraction(14, 4),
        Fraction(10, 6),
        Fraction(6, 2),
        Fraction(4, 2),
        Fraction(2, 1),
    ]
    numeric_value = Fraction(1, 1)
    for factor in chain:
        numeric_value *= factor
    numerical_passed = (numeric_value == 364)
    checks.append({
        "name": "numerical_chain_product",
        "passed": numerical_passed,
        "check_type": "numerical",
        "backend": "numerical",
        "details": f"Product of the hinted factors is {numeric_value}",
    })

    return {
        "proved": all(c["passed"] for c in checks),
        "checks": checks,
    }


if __name__ == "__main__":
    result = verify()
    for chk in result["checks"]:
        print(chk)
    print(result)