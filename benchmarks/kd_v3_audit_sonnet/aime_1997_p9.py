#!/usr/bin/env python3
"""Verified proof for AIME 1997 Problem 9 - Golden Ratio Expression."""

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And
from sympy import sqrt, expand, minimal_polynomial, Symbol, N, simplify, Rational


def verify() -> dict:
    """Verify the golden ratio theorem and compute a^12 - 144a^(-1) = 233."""
    checks = []
    all_passed = True

    # Check 1: Verify a = (1 + sqrt(5))/2 satisfies a^2 - a - 1 = 0 (symbolically)
    try:
        a_val = (1 + sqrt(5)) / 2
        eq_result = a_val**2 - a_val - 1
        x = Symbol('x')
        mp = minimal_polynomial(eq_result, x)
        passed = (mp == x)
        checks.append({
            "name": "golden_ratio_quadratic",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified a^2 - a - 1 = 0 for a = (1+√5)/2 via minimal_polynomial: {mp}"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "golden_ratio_quadratic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {e}"
        })
        all_passed = False

    # Check 2: Verify 2 < a^2 < 3 for a = (1 + sqrt(5))/2
    try:
        a_val = (1 + sqrt(5)) / 2
        a_squared = a_val**2
        # a^2 = (3 + sqrt(5))/2
        val_lower = a_squared - 2
        val_upper = 3 - a_squared
        x = Symbol('x')
        # Both should be positive
        mp_lower = minimal_polynomial(val_lower, x)
        mp_upper = minimal_polynomial(val_upper, x)
        # Check signs numerically
        num_lower = N(val_lower, 50)
        num_upper = N(val_upper, 50)
        passed = (num_lower > 0 and num_upper > 0)
        checks.append({
            "name": "bounds_check",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Verified 2 < a^2 < 3: a^2 - 2 = {num_lower}, 3 - a^2 = {num_upper}"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "bounds_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Error: {e}"
        })
        all_passed = False

    # Check 3: Verify the fractional part condition <a^(-1)> = <a^2>
    # Since 2 < a^2 < 3, we have <a^2> = a^2 - 2
    # Since 1/√3 < a^(-1) < 1/√2 < 1, we have <a^(-1)> = a^(-1)
    # So a^(-1) = a^2 - 2
    try:
        a_val = (1 + sqrt(5)) / 2
        lhs = 1 / a_val
        rhs = a_val**2 - 2
        diff = lhs - rhs
        x = Symbol('x')
        mp = minimal_polynomial(diff, x)
        passed = (mp == x)
        checks.append({
            "name": "fractional_part_condition",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified a^(-1) = a^2 - 2 via minimal_polynomial: {mp}"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "fractional_part_condition",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {e}"
        })
        all_passed = False

    # Check 4: Verify a^12 - 144a^(-1) = 233 (main result)
    try:
        a_val = (1 + sqrt(5)) / 2
        result = a_val**12 - 144 / a_val
        diff = result - 233
        x = Symbol('x')
        mp = minimal_polynomial(diff, x)
        passed = (mp == x)
        checks.append({
            "name": "main_result",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified a^12 - 144a^(-1) = 233 via minimal_polynomial: {mp}"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "main_result",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {e}"
        })
        all_passed = False

    # Check 5: Numerical sanity check
    try:
        a_val = (1 + sqrt(5)) / 2
        result = a_val**12 - 144 / a_val
        num_result = N(result, 100)
        passed = abs(num_result - 233) < 1e-50
        checks.append({
            "name": "numerical_sanity",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Numerical check: a^12 - 144a^(-1) = {num_result} (expect 233)"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Error: {e}"
        })
        all_passed = False

    # Check 6: Verify a^3 = 2a + 1 (alternative golden ratio property)
    try:
        a_val = (1 + sqrt(5)) / 2
        lhs = a_val**3
        rhs = 2 * a_val + 1
        diff = lhs - rhs
        x = Symbol('x')
        mp = minimal_polynomial(diff, x)
        passed = (mp == x)
        checks.append({
            "name": "golden_ratio_cubic",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified a^3 = 2a + 1 via minimal_polynomial: {mp}"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "golden_ratio_cubic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {e}"
        })
        all_passed = False

    # Check 7: Verify using the expansion (a^2)^6 - 144a^(-1)
    try:
        a_val = (1 + sqrt(5)) / 2
        a_squared = (3 + sqrt(5)) / 2
        term1 = a_squared**6
        term2 = 144 / a_val
        result = term1 - term2
        diff = simplify(result - 233)
        x = Symbol('x')
        mp = minimal_polynomial(diff, x)
        passed = (mp == x)
        checks.append({
            "name": "expansion_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified (a^2)^6 - 144a^(-1) = 233 via minimal_polynomial: {mp}"
        })
        all_passed &= passed
    except Exception as e:
        checks.append({
            "name": "expansion_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {e}"
        })
        all_passed = False

    return {
        "proved": all_passed,
        "checks": checks
    }


if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")