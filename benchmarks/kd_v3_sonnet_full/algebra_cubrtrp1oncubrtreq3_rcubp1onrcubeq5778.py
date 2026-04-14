import kdrag as kd
from kdrag.smt import *
from sympy import symbols, cbrt, expand, simplify, N, minimal_polynomial, Rational, sqrt

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Certified algebraic proof using SymPy minimal polynomial
    try:
        # Let u = r^(1/3), so r = u^3
        # Given: u + 1/u = 3
        # Multiply by u: u^2 + 1 = 3u => u^2 - 3u + 1 = 0
        # u is a root of x^2 - 3x + 1 = 0
        # u = (3 ± sqrt(5))/2
        
        u_sym = symbols('u', real=True, positive=True)
        # Take u = (3 + sqrt(5))/2 (positive root)
        u_val = (3 + sqrt(5))/2
        
        # Verify u + 1/u = 3 using minimal polynomial
        expr1 = u_val + 1/u_val - 3
        mp1 = minimal_polynomial(expr1, symbols('x'))
        
        check1_passed = (mp1 == symbols('x'))
        checks.append({
            "name": "verify_u_condition",
            "passed": check1_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial of u + 1/u - 3 is {mp1}, proving u + 1/u = 3 exactly"
        })
        
        if not check1_passed:
            all_passed = False
        
        # Now compute r + 1/r
        # r = u^3, so r + 1/r = u^3 + 1/u^3
        # We know (u + 1/u)^3 = u^3 + 1/u^3 + 3(u + 1/u)
        # 27 = u^3 + 1/u^3 + 9
        # u^3 + 1/u^3 = 18
        r_val = u_val**3
        expr2 = r_val + 1/r_val - 18
        mp2 = minimal_polynomial(expr2, symbols('x'))
        
        check2_passed = (mp2 == symbols('x'))
        checks.append({
            "name": "verify_r_plus_inv_r",
            "passed": check2_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial of r + 1/r - 18 is {mp2}, proving r + 1/r = 18 exactly"
        })
        
        if not check2_passed:
            all_passed = False
        
        # Finally compute r^3 + 1/r^3
        # We know (r + 1/r)^3 = r^3 + 1/r^3 + 3(r + 1/r)
        # 18^3 = r^3 + 1/r^3 + 3*18
        # 5832 = r^3 + 1/r^3 + 54
        # r^3 + 1/r^3 = 5778
        r3_val = r_val**3
        expr3 = r3_val + 1/r3_val - 5778
        mp3 = minimal_polynomial(expr3, symbols('x'))
        
        check3_passed = (mp3 == symbols('x'))
        checks.append({
            "name": "verify_r3_plus_inv_r3",
            "passed": check3_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Minimal polynomial of r^3 + 1/r^3 - 5778 is {mp3}, proving r^3 + 1/r^3 = 5778 exactly"
        })
        
        if not check3_passed:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "symbolic_proof",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in symbolic proof: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Certified proof using kdrag for the integer computation
    try:
        # We proved r + 1/r = 18 symbolically
        # Now prove 18^3 - 54 = 5778 as pure integer arithmetic
        a = Int("a")
        
        # Define the computation: (r + 1/r)^3 - 3(r + 1/r) = r^3 + 1/r^3
        # With r + 1/r = 18: 18^3 - 3*18 = 5778
        thm = kd.prove(18**3 - 54 == 5778)
        
        checks.append({
            "name": "integer_arithmetic_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified proof that 18^3 - 54 = 5778: {thm}"
        })
        
    except Exception as e:
        checks.append({
            "name": "integer_arithmetic_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error in kdrag proof: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Numerical sanity check
    try:
        # Compute numerically with high precision
        u_numeric = N((3 + sqrt(5))/2, 50)
        r_numeric = u_numeric**3
        
        # Verify u + 1/u ≈ 3
        given_check = abs(N(u_numeric + 1/u_numeric, 50) - 3) < 1e-40
        
        # Verify r^3 + 1/r^3 ≈ 5778
        r3_numeric = r_numeric**3
        result_check = abs(N(r3_numeric + 1/r3_numeric, 50) - 5778) < 1e-30
        
        numerical_passed = given_check and result_check
        
        checks.append({
            "name": "numerical_sanity",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"50-digit precision: r^3 + 1/r^3 = {N(r3_numeric + 1/r3_numeric, 15)}"
        })
        
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical error: {str(e)}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Theorem proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")