import kdrag as kd
from kdrag.smt import *
from sympy import symbols, log, simplify, expand, nsimplify, N
from sympy.polys import minimal_polynomial
from sympy import Symbol as SympySymbol

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic algebraic proof using SymPy
    try:
        x_sym, y_sym, z_sym, w_sym = symbols('x y z w', positive=True, real=True)
        
        # Given constraints:
        # log_x(w) = 24 => x^24 = w
        # log_y(w) = 40 => y^40 = w
        # log_{xyz}(w) = 12 => (xyz)^12 = w
        # Need to find: log_z(w) = k => z^k = w
        
        # From the hint, convert to power of 120:
        # x^120 = w^5
        # y^120 = w^3
        # (xyz)^120 = w^10
        
        # The third equation expands to:
        # x^120 * y^120 * z^120 = w^10
        # w^5 * w^3 * z^120 = w^10
        # w^8 * z^120 = w^10
        # z^120 = w^2
        # Therefore z^60 = w
        # So log_z(w) = 60
        
        # Let's verify this algebraically:
        # If z^60 = w, then log_z(w) = 60
        # We'll prove that z^120 - w^2 = 0 given the constraints
        
        # From x^24 = w, we get x = w^(1/24)
        # From y^40 = w, we get y = w^(1/40)
        # From (xyz)^12 = w, we get xyz = w^(1/12)
        
        # Substituting:
        # w^(1/24) * w^(1/40) * z = w^(1/12)
        # z = w^(1/12) / (w^(1/24) * w^(1/40))
        # z = w^(1/12 - 1/24 - 1/40)
        
        # Calculate the exponent:
        from fractions import Fraction
        exponent = Fraction(1, 12) - Fraction(1, 24) - Fraction(1, 40)
        # 1/12 = 10/120, 1/24 = 5/120, 1/40 = 3/120
        # exponent = 10/120 - 5/120 - 3/120 = 2/120 = 1/60
        
        # So z = w^(1/60), which means z^60 = w
        # Therefore log_z(w) = 60
        
        # Verify the fraction calculation
        exp_120 = 120 * exponent
        result_value = int(exp_120)
        
        symbolic_check_passed = (result_value == 2 and exponent == Fraction(1, 60))
        
        checks.append({
            "name": "symbolic_algebraic_derivation",
            "passed": symbolic_check_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Derived z = w^(1/60) from logarithm constraints. Exponent calculation: 1/12 - 1/24 - 1/40 = {exponent} = 1/60, so log_z(w) = 60."
        })
        
        if not symbolic_check_passed:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "symbolic_algebraic_derivation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in symbolic derivation: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify using SymPy that the algebraic identity holds
    try:
        t = SympySymbol('t', real=True, positive=True)
        
        # Verify that if z = w^(1/60), then all constraints are satisfied
        # Set w = t (parameter)
        w_val = t
        x_val = w_val**Fraction(1, 24)  # x^24 = w
        y_val = w_val**Fraction(1, 40)  # y^40 = w
        z_val = w_val**Fraction(1, 60)  # Our claim: z^60 = w
        
        # Check constraint 3: (xyz)^12 = w
        product = x_val * y_val * z_val
        product_to_12 = product**12
        product_to_12_simplified = simplify(expand(product_to_12 / w_val))
        
        # This should equal 1 (i.e., product^12 / w = 1)
        expr = product_to_12_simplified - 1
        expr_simplified = simplify(expr)
        
        # Check if it's symbolically zero
        is_zero = expr_simplified == 0
        
        checks.append({
            "name": "constraint_verification",
            "passed": is_zero,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified that z = w^(1/60) satisfies (xyz)^12 = w. Simplified expression: {expr_simplified}"
        })
        
        if not is_zero:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "constraint_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in constraint verification: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Numerical verification with concrete values
    try:
        import math
        
        # Choose w = 2^120 for clean calculations
        w_concrete = 2.0**120
        
        # From constraints:
        x_concrete = w_concrete**(1/24)  # x^24 = w
        y_concrete = w_concrete**(1/40)  # y^40 = w
        
        # Verify first two constraints
        check1 = abs(x_concrete**24 - w_concrete) < 1e-6 * w_concrete
        check2 = abs(y_concrete**40 - w_concrete) < 1e-6 * w_concrete
        
        # From (xyz)^12 = w, solve for z
        xyz_val = w_concrete**(1/12)
        z_concrete = xyz_val / (x_concrete * y_concrete)
        
        # Check if z^60 = w
        z_to_60 = z_concrete**60
        check3 = abs(z_to_60 - w_concrete) / w_concrete < 1e-9
        
        # Verify log_z(w)
        log_z_w = math.log(w_concrete) / math.log(z_concrete)
        check4 = abs(log_z_w - 60.0) < 1e-9
        
        numerical_passed = check1 and check2 and check3 and check4
        
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Concrete test with w=2^120: log_z(w) = {log_z_w:.10f}, expected 60. All constraint checks: {check1 and check2 and check3}"
        })
        
        if not numerical_passed:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error in numerical verification: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Alternative numerical verification with different base
    try:
        import math
        
        # Use w = e^120 for variety
        w_test = math.e**120
        
        x_test = w_test**(1/24)
        y_test = w_test**(1/40)
        z_test_from_xyz = (w_test**(1/12)) / (x_test * y_test)
        
        log_z_w_test = math.log(w_test) / math.log(z_test_from_xyz)
        
        test_passed = abs(log_z_w_test - 60.0) < 1e-9
        
        checks.append({
            "name": "alternative_numerical_test",
            "passed": test_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Alternative test with w=e^120: log_z(w) = {log_z_w_test:.10f}"
        })
        
        if not test_passed:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "alternative_numerical_test",
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
    print(f"Proof verified: {result['proved']}")
    print("\nDetailed checks:")
    for check in result['checks']:
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}):")
        print(f"  {check['details']}")
    
    if result['proved']:
        print("\n" + "="*60)
        print("THEOREM PROVED: log_z(w) = 60")
        print("="*60)
    else:
        print("\nProof incomplete or failed.")