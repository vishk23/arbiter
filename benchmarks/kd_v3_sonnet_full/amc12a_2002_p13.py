import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, sqrt, simplify, minimal_polynomial, Rational

def verify():
    checks = []
    all_passed = True
    
    # ===== SYMBOLIC VERIFICATION WITH SYMPY =====
    # The problem requires |x - 1/x| = 1, which gives two cases:
    # Case 1: x - 1/x = 1 => x^2 - x - 1 = 0
    # Case 2: 1/x - x = 1 => -x^2 + 1 - x = 0 => x^2 + x - 1 = 0
    
    # Solutions to x^2 - x - 1 = 0: x = (1 ± sqrt(5))/2
    # Solutions to x^2 + x - 1 = 0: x = (-1 ± sqrt(5))/2
    
    # Positive solutions:
    a = (Rational(-1) + sqrt(5)) / 2  # from x^2 + x - 1 = 0
    b = (Rational(1) + sqrt(5)) / 2   # from x^2 - x - 1 = 0
    
    # Check 1: Verify a satisfies the difference condition
    check1_name = "verify_a_satisfies_condition"
    try:
        diff_a = a - 1/a
        diff_a_simplified = simplify(diff_a)
        # Should be either 1 or -1
        x = Symbol('x')
        mp_a_plus1 = minimal_polynomial(diff_a_simplified - 1, x)
        mp_a_minus1 = minimal_polynomial(diff_a_simplified + 1, x)
        
        passed_a = (mp_a_plus1 == x or mp_a_minus1 == x)
        checks.append({
            "name": check1_name,
            "passed": passed_a,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"a = (-1+sqrt(5))/2 satisfies |a - 1/a| = 1. Diff = {diff_a_simplified}, minimal_poly(diff-1) = {mp_a_plus1}, minimal_poly(diff+1) = {mp_a_minus1}"
        })
        all_passed = all_passed and passed_a
    except Exception as e:
        checks.append({
            "name": check1_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error verifying a: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify b satisfies the difference condition
    check2_name = "verify_b_satisfies_condition"
    try:
        diff_b = b - 1/b
        diff_b_simplified = simplify(diff_b)
        x = Symbol('x')
        mp_b_plus1 = minimal_polynomial(diff_b_simplified - 1, x)
        mp_b_minus1 = minimal_polynomial(diff_b_simplified + 1, x)
        
        passed_b = (mp_b_plus1 == x or mp_b_minus1 == x)
        checks.append({
            "name": check2_name,
            "passed": passed_b,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"b = (1+sqrt(5))/2 satisfies |b - 1/b| = 1. Diff = {diff_b_simplified}, minimal_poly(diff-1) = {mp_b_plus1}, minimal_poly(diff+1) = {mp_b_minus1}"
        })
        all_passed = all_passed and passed_b
    except Exception as e:
        checks.append({
            "name": check2_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error verifying b: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify a + b = sqrt(5) using minimal polynomial
    check3_name = "verify_sum_equals_sqrt5"
    try:
        sum_ab = a + b
        sum_simplified = simplify(sum_ab)
        x = Symbol('x')
        # If sum_simplified = sqrt(5), then sum_simplified - sqrt(5) = 0
        mp = minimal_polynomial(sum_simplified - sqrt(5), x)
        passed_sum = (mp == x)
        checks.append({
            "name": check3_name,
            "passed": passed_sum,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"a + b = {sum_simplified}. Minimal polynomial of (a+b - sqrt(5)) is {mp}, which equals x: {passed_sum}. This rigorously proves a+b = sqrt(5)."
        })
        all_passed = all_passed and passed_sum
    except Exception as e:
        checks.append({
            "name": check3_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error verifying sum: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify a and b are distinct positive numbers
    check4_name = "verify_distinct_positive"
    try:
        from sympy import N
        a_num = N(a, 50)
        b_num = N(b, 50)
        distinct = abs(a_num - b_num) > 1e-40
        positive = (a_num > 0 and b_num > 0)
        passed_distinct = distinct and positive
        checks.append({
            "name": check4_name,
            "passed": passed_distinct,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"a ≈ {a_num}, b ≈ {b_num}, distinct: {distinct}, both positive: {positive}"
        })
        all_passed = all_passed and passed_distinct
    except Exception as e:
        checks.append({
            "name": check4_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error checking distinctness: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Numerical sanity check on the difference condition
    check5_name = "numerical_sanity_check"
    try:
        from sympy import N, Abs
        a_num = N(a, 50)
        b_num = N(b, 50)
        diff_a_num = abs(N(a - 1/a, 50) - 1)
        diff_b_num = abs(N(b - 1/b, 50) - 1)
        # Also check the negative case
        diff_a_num_neg = abs(N(a - 1/a, 50) + 1)
        diff_b_num_neg = abs(N(b - 1/b, 50) + 1)
        
        tol = 1e-40
        passed_numerical = ((diff_a_num < tol or diff_a_num_neg < tol) and 
                           (diff_b_num < tol or diff_b_num_neg < tol))
        checks.append({
            "name": check5_name,
            "passed": passed_numerical,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical: |a - 1/a - 1| = {diff_a_num}, |a - 1/a + 1| = {diff_a_num_neg}, |b - 1/b - 1| = {diff_b_num}, |b - 1/b + 1| = {diff_b_num_neg} (all < {tol})"
        })
        all_passed = all_passed and passed_numerical
    except Exception as e:
        checks.append({
            "name": check5_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error in numerical check: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} [{check['backend']}/{check['proof_type']}]")
        print(f"  {check['details']}")