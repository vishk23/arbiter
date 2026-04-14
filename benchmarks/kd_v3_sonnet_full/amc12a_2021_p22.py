import kdrag as kd
from kdrag.smt import *
from sympy import cos, pi, Rational, simplify, expand, Symbol, minimal_polynomial, N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: CERTIFIED proof that abc = 1/32 using minimal polynomial
    try:
        x_sym = Symbol('x')
        
        # Define the roots
        r1 = cos(2*pi/7)
        r2 = cos(4*pi/7)
        r3 = cos(6*pi/7)
        
        # By Vieta's formulas for P(x) = x^3 + ax^2 + bx + c:
        # a = -(r1 + r2 + r3)
        # b = r1*r2 + r1*r3 + r2*r3
        # c = -r1*r2*r3
        
        a_val = -(r1 + r2 + r3)
        b_val = r1*r2 + r1*r3 + r2*r3
        c_val = -r1*r2*r3
        
        # Compute abc
        abc_sym = a_val * b_val * c_val
        
        # RIGOROUS PROOF: Use minimal polynomial to prove abc - 1/32 = 0
        expr = abc_sym - Rational(1, 32)
        mp = minimal_polynomial(expr, x_sym)
        
        # If mp == x, then expr is algebraically zero (CERTIFIED PROOF)
        passed = (mp == x_sym)
        
        checks.append({
            "name": "vieta_abc_certified_proof",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"CERTIFIED: minimal_polynomial(abc - 1/32, x) = {mp}. This proves abc = 1/32 exactly via algebraic number theory."
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "vieta_abc_certified_proof",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Error in certified proof: {str(e)}"
        })
        all_passed = False
    
    # Check 2: CERTIFIED proof that sum of roots = 1/2 using minimal polynomial
    try:
        r1 = cos(2*pi/7)
        r2 = cos(4*pi/7)
        r3 = cos(6*pi/7)
        
        # Sum of roots should equal -a, and we know a should be -1/2
        sum_roots = r1 + r2 + r3
        expr = sum_roots - Rational(1, 2)
        
        mp = minimal_polynomial(expr, x_sym)
        passed = (mp == x_sym)
        
        checks.append({
            "name": "sum_of_roots_certified",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"CERTIFIED: minimal_polynomial(sum_of_roots - 1/2, x) = {mp}. Proves a = -1/2."
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "sum_of_roots_certified",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: CERTIFIED proof that product of pairwise sums = -1/8
    try:
        r1 = cos(2*pi/7)
        r2 = cos(4*pi/7)
        r3 = cos(6*pi/7)
        
        # b = r1*r2 + r1*r3 + r2*r3
        b_val = r1*r2 + r1*r3 + r2*r3
        expr = b_val - Rational(-1, 8)
        
        mp = minimal_polynomial(expr, x_sym)
        passed = (mp == x_sym)
        
        checks.append({
            "name": "pairwise_products_certified",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"CERTIFIED: minimal_polynomial(b - (-1/8), x) = {mp}. Proves b = -1/8."
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "pairwise_products_certified",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: CERTIFIED proof that product of roots = 1/8
    try:
        r1 = cos(2*pi/7)
        r2 = cos(4*pi/7)
        r3 = cos(6*pi/7)
        
        # c = -r1*r2*r3, so r1*r2*r3 should equal -c = 1/8
        prod_roots = r1*r2*r3
        expr = prod_roots - Rational(1, 8)
        
        mp = minimal_polynomial(expr, x_sym)
        passed = (mp == x_sym)
        
        checks.append({
            "name": "product_of_roots_certified",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"CERTIFIED: minimal_polynomial(r1*r2*r3 - 1/8, x) = {mp}. Proves c = -1/8."
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "product_of_roots_certified",
            "passed": False,
            "backend": "sympy",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Numerical sanity check with high precision
    try:
        r1 = cos(2*pi/7)
        r2 = cos(4*pi/7)
        r3 = cos(6*pi/7)
        
        a_val = -(r1 + r2 + r3)
        b_val = r1*r2 + r1*r3 + r2*r3
        c_val = -r1*r2*r3
        
        abc_numerical = N(a_val * b_val * c_val, 50)
        expected = N(Rational(1, 32), 50)
        
        diff = abs(abc_numerical - expected)
        passed = diff < 1e-40
        
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"50-digit precision: abc = {abc_numerical}, expected = {expected}, diff = {diff}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
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
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"[{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")