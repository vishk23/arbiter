import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Or
from sympy import symbols, sqrt, minimal_polynomial, expand, simplify, Rational, N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify a = (1 + sqrt(5))/2 satisfies a^3 - 2a - 1 = 0
    a_sym = symbols('a', real=True, positive=True)
    phi = (1 + sqrt(5)) / 2
    cubic_eq = phi**3 - 2*phi - 1
    cubic_simplified = simplify(cubic_eq)
    
    x = symbols('x')
    mp = minimal_polynomial(cubic_simplified, x)
    check1_passed = (mp == x)
    
    checks.append({
        "name": "cubic_equation_proof",
        "passed": check1_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Proved phi^3 - 2*phi - 1 = 0 via minimal_polynomial: {mp} == x is {check1_passed}"
    })
    all_passed = all_passed and check1_passed
    
    # Check 2: Verify 2 < a^2 < 3
    phi_squared = phi**2
    phi_sq_val = float(phi_squared.evalf())
    check2_passed = 2 < phi_sq_val < 3
    
    checks.append({
        "name": "range_constraint",
        "passed": check2_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Verified 2 < phi^2 < 3: phi^2 = {phi_sq_val}, check: {check2_passed}"
    })
    all_passed = all_passed and check2_passed
    
    # Check 3: Verify phi^2 - 2 = phi^(-1)
    lhs = phi**2 - 2
    rhs = 1/phi
    diff = simplify(lhs - rhs)
    mp3 = minimal_polynomial(diff, x)
    check3_passed = (mp3 == x)
    
    checks.append({
        "name": "fractional_part_property",
        "passed": check3_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Proved phi^2 - 2 = 1/phi via minimal_polynomial: {mp3} == x is {check3_passed}"
    })
    all_passed = all_passed and check3_passed
    
    # Check 4: Compute a^12 - 144*a^(-1) symbolically
    result_expr = phi**12 - 144/phi
    result_simplified = simplify(result_expr)
    
    # Verify it equals 233
    diff_from_233 = simplify(result_simplified - 233)
    mp4 = minimal_polynomial(diff_from_233, x)
    check4_passed = (mp4 == x)
    
    checks.append({
        "name": "final_answer_proof",
        "passed": check4_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Proved phi^12 - 144/phi = 233 via minimal_polynomial: {mp4} == x is {check4_passed}. Simplified result: {result_simplified}"
    })
    all_passed = all_passed and check4_passed
    
    # Check 5: Numerical verification of final answer
    result_numerical = float(phi**12 - 144/phi)
    check5_passed = abs(result_numerical - 233.0) < 1e-10
    
    checks.append({
        "name": "final_answer_numerical",
        "passed": check5_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Numerical check: phi^12 - 144/phi = {result_numerical}, difference from 233: {abs(result_numerical - 233.0)}"
    })
    all_passed = all_passed and check5_passed
    
    # Check 6: Verify using phi properties: phi^2 = phi + 1
    phi_sq_identity = phi**2 - phi - 1
    mp6 = minimal_polynomial(simplify(phi_sq_identity), x)
    check6_passed = (mp6 == x)
    
    checks.append({
        "name": "golden_ratio_property",
        "passed": check6_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Proved phi^2 = phi + 1 via minimal_polynomial: {mp6} == x is {check6_passed}"
    })
    all_passed = all_passed and check6_passed
    
    # Check 7: Alternative computation using phi^2 = phi + 1
    # Build phi^12 step by step
    phi_2 = phi + 1  # From phi^2 = phi + 1
    phi_3 = simplify(phi_2 * phi)  # = 2*phi + 1
    phi_3_check = simplify(phi_3 - (2*phi + 1))
    mp7a = minimal_polynomial(phi_3_check, x)
    
    phi_6 = simplify(phi_3**2)
    phi_12 = simplify(phi_6**2)
    
    # Now compute the final answer
    final_alt = simplify(phi_12 - 144/phi)
    diff_alt = simplify(final_alt - 233)
    mp7 = minimal_polynomial(diff_alt, x)
    check7_passed = (mp7 == x and mp7a == x)
    
    checks.append({
        "name": "alternative_computation",
        "passed": check7_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Alternative computation using phi^2=phi+1: verified phi^3=2phi+1 ({mp7a==x}), final result ({mp7==x})"
    })
    all_passed = all_passed and check7_passed
    
    # Check 8: Verify (a^2)^6 expansion as in hint
    a2 = (3 + sqrt(5))/2  # This is phi^2
    a2_check = simplify(a2 - phi**2)
    mp8a = minimal_polynomial(a2_check, x)
    
    a2_6th = a2**6
    a2_6th_simplified = simplify(a2_6th)
    
    # Should be 161 + 72*sqrt(5)
    expected_first_term = 161 + 72*sqrt(5)
    diff_8 = simplify(a2_6th_simplified - expected_first_term)
    mp8 = minimal_polynomial(diff_8, x)
    check8_passed = (mp8 == x and mp8a == x)
    
    checks.append({
        "name": "binomial_expansion_verification",
        "passed": check8_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Verified (phi^2)^6 = 161 + 72*sqrt(5): a2=phi^2 check ({mp8a==x}), expansion check ({mp8==x})"
    })
    all_passed = all_passed and check8_passed
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof verified: {result['proved']}")
    print(f"\nCheck details:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['passed']}")
        print(f"  {check['details']}")