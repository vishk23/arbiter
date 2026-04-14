import kdrag as kd
from kdrag.smt import *
from sympy import sqrt, log, N, simplify, expand, Symbol, minimal_polynomial, Rational
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic verification using SymPy
    # We'll prove that log_2(6) + log_3(6) = (sqrt(log_2(3)) + sqrt(log_3(2)))^2
    try:
        # Define the logarithms symbolically
        # log_2(6) = log(6)/log(2), log_3(6) = log(6)/log(3)
        log2_6 = log(6, 2)
        log3_6 = log(6, 3)
        log2_3 = log(3, 2)
        log3_2 = log(2, 3)
        
        # LHS: log_2(6) + log_3(6)
        lhs = log2_6 + log3_6
        
        # Using log_b(uv) = log_b(u) + log_b(v):
        # log_2(6) = log_2(2*3) = log_2(2) + log_2(3) = 1 + log_2(3)
        # log_3(6) = log_3(2*3) = log_3(2) + log_3(3) = log_3(2) + 1
        expanded_lhs = 2 + log2_3 + log3_2
        
        # RHS: (sqrt(log_2(3)) + sqrt(log_3(2)))^2
        rhs_expanded = (sqrt(log2_3) + sqrt(log3_2))**2
        rhs_expanded_form = expand(rhs_expanded)
        # This should equal: log_2(3) + 2*sqrt(log_2(3)*log_3(2)) + log_3(2)
        
        # Key insight: log_2(3) * log_3(2) = 1 (change of base identity)
        # So 2*sqrt(log_2(3)*log_3(2)) = 2*sqrt(1) = 2
        
        # Verify log_b(a) * log_a(b) = 1
        product = log2_3 * log3_2
        product_simplified = simplify(product)
        
        # Check if product equals 1
        diff_product = simplify(product_simplified - 1)
        assert abs(N(diff_product)) < 1e-10, f"Product identity failed: {product_simplified}"
        
        # Now verify the full equation
        # LHS = log_2(6) + log_3(6) = 2 + log_2(3) + log_3(2)
        # RHS^2 = log_2(3) + 2*sqrt(log_2(3)*log_3(2)) + log_3(2)
        #       = log_2(3) + 2*1 + log_3(2) = 2 + log_2(3) + log_3(2)
        
        lhs_simplified = simplify(lhs)
        rhs_squared = simplify(rhs_expanded_form)
        
        diff = simplify(lhs_simplified - rhs_squared)
        
        # Numerical check
        diff_numeric = abs(N(diff))
        assert diff_numeric < 1e-10, f"Equation verification failed: diff = {diff_numeric}"
        
        checks.append("symbolic_verification")
        print("Check 1 passed: Symbolic verification successful")
        print(f"  log_2(6) + log_3(6) = {N(lhs_simplified)}")
        print(f"  (sqrt(log_2(3)) + sqrt(log_3(2)))^2 = {N(rhs_squared)}")
        print(f"  Difference: {diff_numeric}")
        
    except Exception as e:
        all_passed = False
        print(f"Check 1 FAILED: {e}")
    
    # Check 2: Numerical verification
    try:
        lhs_val = N(log(6, 2) + log(6, 3))
        rhs_val = N((sqrt(log(3, 2)) + sqrt(log(2, 3)))**2)
        
        diff_val = abs(lhs_val - rhs_val)
        assert diff_val < 1e-10, f"Numerical verification failed: diff = {diff_val}"
        
        checks.append("numerical_verification")
        print("Check 2 passed: Numerical verification successful")
        print(f"  LHS = {lhs_val}")
        print(f"  RHS^2 = {rhs_val}")
        
    except Exception as e:
        all_passed = False
        print(f"Check 2 FAILED: {e}")
    
    return all_passed, checks

if __name__ == "__main__":
    passed, check_names = verify()
    print(f"\nAll checks passed: {passed}")
    print(f"Checks: {check_names}")