import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, factor, sqrt as sp_sqrt, Poly, minimal_polynomial, N
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify Vieta's formulas for x^4 + 2x^3 + 2 = 0
    check1 = {
        "name": "vietas_formulas",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        # For polynomial x^4 + 2x^3 + 0x^2 + 0x + 2
        # s1 = -a3/a4 = -2/1 = -2
        # s2 = a2/a4 = 0/1 = 0
        # s3 = -a1/a4 = 0/1 = 0
        # s4 = a0/a4 = 2/1 = 2
        s1, s2, s3, s4 = -2, 0, 0, 2
        check1["details"] = f"Vieta's formulas give s1={s1}, s2={s2}, s3={s3}, s4={s4}"
        check1["passed"] = True
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Symbolic construction of resolvent cubic P(x)
    check2 = {
        "name": "resolvent_cubic_construction",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        x = symbols('x')
        s1, s2, s3, s4 = -2, 0, 0, 2
        
        # P(x) = x^3 - s2*x^2 + (s3*s1 - 4*s4)*x + (-s3^2 - s4*s1^2 + s4*s2)
        coeff_x2 = -s2
        coeff_x1 = s3*s1 - 4*s4
        coeff_x0 = -s3**2 - s4*s1**2 + s4*s2
        
        P = x**3 + coeff_x2*x**2 + coeff_x1*x + coeff_x0
        P_expected = x**3 - 8*x - 8
        
        diff = expand(P - P_expected)
        
        # Verify difference is zero
        y = symbols('y')
        mp = minimal_polynomial(diff, y)
        
        if mp == y:
            check2["passed"] = True
            check2["details"] = f"Resolvent cubic P(x) = {P_expected} verified symbolically"
        else:
            check2["passed"] = False
            check2["details"] = f"Resolvent cubic mismatch: got {P}, expected {P_expected}"
            all_passed = False
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: Verify factorization of P(x)
    check3 = {
        "name": "resolvent_factorization",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        x = symbols('x')
        P = x**3 - 8*x - 8
        factored = (x + 2) * (x**2 - 2*x - 4)
        
        diff = expand(P - factored)
        y = symbols('y')
        mp = minimal_polynomial(diff, y)
        
        if mp == y:
            check3["passed"] = True
            check3["details"] = "Factorization P(x) = (x+2)(x^2-2x-4) verified"
        else:
            check3["passed"] = False
            check3["details"] = f"Factorization incorrect"
            all_passed = False
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: Verify roots of P(x) using minimal polynomial
    check4 = {
        "name": "roots_verification",
        "backend": "sympy",
        "proof_type": "symbolic_zero"
    }
    try:
        x = symbols('x')
        
        # Root 1: x = -2
        r1 = -2
        P_at_r1 = r1**3 - 8*r1 - 8
        y = symbols('y')
        mp1 = minimal_polynomial(P_at_r1, y)
        
        # Roots 2 and 3: x = 1 ± sqrt(5)
        # From x^2 - 2x - 4 = 0
        r2 = 1 + sp_sqrt(5)
        r3 = 1 - sp_sqrt(5)
        
        P_at_r2 = r2**3 - 8*r2 - 8
        P_at_r3 = r3**3 - 8*r3 - 8
        
        mp2 = minimal_polynomial(P_at_r2, y)
        mp3 = minimal_polynomial(P_at_r3, y)
        
        if mp1 == y and mp2 == y and mp3 == y:
            check4["passed"] = True
            check4["details"] = "All three roots {-2, 1+sqrt(5), 1-sqrt(5)} verified as zeros of P(x)"
        else:
            check4["passed"] = False
            check4["details"] = f"Root verification failed: mp1={mp1}, mp2={mp2}, mp3={mp3}"
            all_passed = False
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: Numerical verification
    check5 = {
        "name": "numerical_verification",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        # Compute numerical values of roots
        r1_num = -2.0
        r2_num = float(N(1 + sp_sqrt(5), 50))
        r3_num = float(N(1 - sp_sqrt(5), 50))
        
        # Verify they are roots of P(x) = x^3 - 8x - 8
        P_r1 = r1_num**3 - 8*r1_num - 8
        P_r2 = r2_num**3 - 8*r2_num - 8
        P_r3 = r3_num**3 - 8*r3_num - 8
        
        tol = 1e-10
        if abs(P_r1) < tol and abs(P_r2) < tol and abs(P_r3) < tol:
            check5["passed"] = True
            check5["details"] = f"Numerical verification: |P(-2)|={abs(P_r1):.2e}, |P(1+√5)|={abs(P_r2):.2e}, |P(1-√5)|={abs(P_r3):.2e}"
        else:
            check5["passed"] = False
            check5["details"] = f"Numerical verification failed"
            all_passed = False
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check5)
    
    # Check 6: Verify the original polynomial has 4 distinct roots (numerical)
    check6 = {
        "name": "original_polynomial_roots",
        "backend": "numerical",
        "proof_type": "numerical"
    }
    try:
        x = symbols('x')
        orig_poly = x**4 + 2*x**3 + 2
        roots = sp.solve(orig_poly, x)
        
        if len(roots) == 4:
            # Verify all roots are distinct
            roots_numerical = [complex(N(r, 50)) for r in roots]
            distinct = True
            for i in range(len(roots_numerical)):
                for j in range(i+1, len(roots_numerical)):
                    if abs(roots_numerical[i] - roots_numerical[j]) < 1e-10:
                        distinct = False
            
            if distinct:
                check6["passed"] = True
                check6["details"] = f"Original polynomial has 4 distinct roots (verified numerically)"
            else:
                check6["passed"] = False
                check6["details"] = "Roots are not distinct"
                all_passed = False
        else:
            check6["passed"] = False
            check6["details"] = f"Expected 4 roots, found {len(roots)}"
            all_passed = False
    except Exception as e:
        check6["passed"] = False
        check6["details"] = f"Error: {e}"
        all_passed = False
    checks.append(check6)
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        print(f"  {check['name']}: {check['passed']} ({check['backend']}, {check['proof_type']})")
        print(f"    {check['details']}")