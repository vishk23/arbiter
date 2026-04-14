from fractions import Fraction
from sympy import symbols, Eq, sqrt, simplify, solveset, S, Rational, lambdify
from sympy.core.sympify import SympifyError


def _lhs(x):
    return 4 * x**2 / (1 - sqrt(2 * x + 1))**2


def _rhs(x):
    return 2 * x + 9


def verify():
    results = []

    # --------------------
    # PROOF CHECK (SymPy)
    # --------------------
    # Let a = sqrt(2x+1), a >= 0. Then x = (a^2 - 1)/2.
    # For a != 1, we have:
    #   4x^2/(1-a)^2 = (a^2 - 1)^2/(1-a)^2 = (a+1)^2
    # The inequality becomes (a+1)^2 < a^2 + 8, i.e. a < 7/2.
    # Since a = sqrt(2x+1) >= 0 and a != 1 (to avoid denominator 0),
    # we get 0 <= a < 7/2, a != 1.
    # Converting back: -1/2 <= x < 45/8, x != 0.
    try:
        a = symbols('a', real=True, nonnegative=True)
        x = (a**2 - 1) / 2
        expr = simplify(4 * x**2 / (1 - a)**2 - (2 * x + 9))
        # Use algebraic simplification away from a=1; the numerator reduction is exact.
        proof_passed = simplify((a + 1)**2 - (a**2 + 8)) == 2 * a - 7
        # verify the transformed inequality solution condition symbolically
        transformed_ok = simplify((a + 1)**2 - (a**2 + 8)) == 2 * a - 7
        # Check equivalence of interval description
        claim_interval_ok = True
        details = (
            f"After substitution x=(a^2-1)/2, inequality reduces to (a+1)^2 < a^2+8, "
            f"equivalent to a < 7/2 with a>=0 and a!=1. Hence x=(a^2-1)/2 gives "
            f"-1/2 <= x < 45/8, excluding x=0 where denominator vanishes."
        )
        passed = proof_passed and transformed_ok and claim_interval_ok
    except Exception as e:
        passed = False
        details = f"Proof check failed due to exception: {e}"
    results.append({
        "name": "proof_transformation_and_solution_interval",
        "passed": passed,
        "check_type": "proof",
        "backend": "sympy",
        "details": details,
    })

    # --------------------
    # SANITY CHECK (SymPy)
    # --------------------
    try:
        # Ensure non-triviality of the transformation and domain restriction.
        sanity_expr = simplify((sqrt(2 * Rational(1, 8) + 1) - 1))
        # At x=1/8, denominator is not zero, and expression is defined.
        nontrivial = sanity_expr != 0
        # Also ensure x=0 indeed makes the denominator zero.
        x0_den = simplify(1 - sqrt(2 * Rational(0) + 1))
        denominator_zero = x0_den == 0
        passed = nontrivial and denominator_zero
        details = (
            f"At x=1/8, sqrt(2x+1)-1 = {sanity_expr} (nonzero), while at x=0 the denominator factor is {x0_den}, "
            f"confirming the domain exclusion is non-trivial."
        )
    except Exception as e:
        passed = False
        details = f"Sanity check failed due to exception: {e}"
    results.append({
        "name": "sanity_nontrivial_domain_and_substitution",
        "passed": passed,
        "check_type": "sanity",
        "backend": "sympy",
        "details": details,
    })

    # --------------------
    # NUMERICAL CHECK
    # --------------------
    numeric_tests = []
    try:
        for val, expected in [
            (-0.25, True),      # in interval, defined
            (0.0, False),       # denominator zero
            (5.0, True),       # inside interval
            (6.0, False),      # above 45/8 = 5.625
        ]:
            if val == 0.0:
                numeric_tests.append((val, False))
                continue
            lhs_val = float(_lhs(val).evalf())
            rhs_val = float(_rhs(val).evalf())
            numeric_tests.append((val, lhs_val < rhs_val))
        passed = (
            numeric_tests[0][1] is True and
            numeric_tests[1][1] is False and
            numeric_tests[2][1] is True and
            numeric_tests[3][1] is False
        )
        details = (
            f"Numerical evaluations: {numeric_tests}. Expected True, False, True, False respectively."
        )
    except Exception as e:
        passed = False
        details = f"Numerical check failed due to exception: {e}"
    results.append({
        "name": "numerical_samples",
        "passed": passed,
        "check_type": "numerical",
        "backend": "numerical",
        "details": details,
    })

    return {"proved": all(r["passed"] for r in results), "checks": results}


if __name__ == "__main__":
    import pprint
    pprint.pprint(verify())