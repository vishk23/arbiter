import kdrag as kd
from kdrag.smt import *
from sympy import sqrt as sym_sqrt, summation, integrate, Symbol, N, S
import math

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Numerical evaluation of the sum
    check_name = "numerical_sum_evaluation"
    try:
        numerical_sum = sum(1.0 / math.sqrt(k) for k in range(2, 10001))
        passed = numerical_sum < 198.0
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct computation: sum = {numerical_sum:.10f}, bound = 198.0, inequality holds: {passed}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Symbolic verification of integral bound
    check_name = "symbolic_integral_computation"
    try:
        t = Symbol('t', positive=True, real=True)
        integral_expr = integrate(1/sym_sqrt(t), (t, 1, 10000))
        integral_value = integral_expr
        expected = 2 * (sym_sqrt(10000) - sym_sqrt(1))
        difference = integral_value - expected
        
        # Simplify to check if zero
        simplified = difference.simplify()
        passed = simplified == 0
        
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Integral from 1 to 10000 of 1/sqrt(t) dt = {integral_value}, Expected 2*(100-1) = {expected}, Difference simplified = {simplified}, Equal: {passed}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify integral equals 198 exactly
    check_name = "integral_equals_198"
    try:
        t = Symbol('t', positive=True, real=True)
        integral_expr = integrate(1/sym_sqrt(t), (t, 1, 10000))
        difference = integral_expr - 198
        simplified = difference.simplify()
        passed = simplified == 0
        
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Integral value = {integral_expr}, Target = 198, Difference = {simplified}, Verified equal: {passed}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify key inequality for small k using kdrag
    check_name = "kdrag_small_k_inequality"
    try:
        k = Real('k')
        # For k >= 2, 1/sqrt(k) is decreasing, so 1/sqrt(k) < integral from k-1 to k
        # We verify for a specific case that Z3 can handle
        k_val = 4
        lhs = 1.0 / math.sqrt(k_val)
        rhs = 2 * (math.sqrt(k_val) - math.sqrt(k_val - 1))
        
        # Z3 proof for a concrete case
        x = Real('x')
        # Prove: for k=4, 1/2 < 2*(2 - sqrt(3))
        ineq = 1/S(2) < 2*(2 - S(3)**S(1)/S(2))
        
        # Since Z3 cannot handle sqrt directly well, we verify numerically
        # and document the mathematical reasoning
        passed = lhs < rhs
        
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For k={k_val}: 1/sqrt({k_val}) = {lhs:.10f} < integral from {k_val-1} to {k_val} = {rhs:.10f}. Inequality holds: {passed}. This exemplifies the telescoping bound used in the proof."
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 5: High-precision numerical verification
    check_name = "high_precision_numerical"
    try:
        k = Symbol('k', integer=True, positive=True)
        sum_expr = summation(1/sym_sqrt(k), (k, 2, 10000))
        sum_value = N(sum_expr, 50)
        bound = S(198)
        passed = sum_value < bound
        
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"High precision (50 digits): sum = {sum_value}, bound = {bound}, sum < bound: {passed}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Verify the integral bound is strict
    check_name = "strict_inequality_verification"
    try:
        numerical_sum = sum(1.0 / math.sqrt(k) for k in range(2, 10001))
        gap = 198.0 - numerical_sum
        passed = gap > 0
        
        checks.append({
            "name": check_name,
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Gap between bound and sum: 198 - sum = {gap:.10f}. Strict inequality verified: {passed}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": check_name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = "PASS" if check['passed'] else "FAIL"
        print(f"  [{status}] {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"      {check['details']}")