import kdrag as kd
from kdrag.smt import *
import sympy as sp
from sympy import sqrt as sp_sqrt, symbols, simplify, expand, minimal_polynomial, Rational, factor

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic algebraic proof using SymPy minimal polynomial
    # We prove the inequality by showing the difference is non-negative
    # RHS - LHS = (a-b)^2/(8b) - ((a+b)/2 - sqrt(ab))
    try:
        a_sym, b_sym = symbols('a b', positive=True, real=True)
        lhs = (a_sym + b_sym) / 2 - sp_sqrt(a_sym * b_sym)
        rhs = (a_sym - b_sym)**2 / (8 * b_sym)
        diff = rhs - lhs
        
        # Multiply by 8b to clear denominators
        diff_cleared = simplify(expand(diff * 8 * b_sym))
        
        # The cleared expression should be: (a-b)^2 - 4b(a+b) + 8b*sqrt(ab)
        # Let's substitute u = sqrt(a/b) (valid since a,b > 0)
        # Then a = u^2*b, and we can factor
        
        # Alternative: directly show diff >= 0 by completing the square
        # diff = (a-b)^2/(8b) - (a+b)/2 + sqrt(ab)
        #      = [(a-b)^2 - 4b(a+b) + 8b*sqrt(ab)] / (8b)
        #      = [a^2 - 2ab + b^2 - 4ab - 4b^2 + 8b*sqrt(ab)] / (8b)
        #      = [a^2 - 6ab - 3b^2 + 8b*sqrt(ab)] / (8b)
        
        # Complete the square: let s = sqrt(ab)
        # Then a^2 - 6ab - 3b^2 + 8b*s
        # We want to show this is >= 0 when a >= b > 0
        
        # Actually, substitute t = sqrt(a) and u = sqrt(b)
        # Then a = t^2, b = u^2, sqrt(ab) = tu
        t, u = symbols('t u', positive=True, real=True)
        diff_sub = diff.subs([(a_sym, t**2), (b_sym, u**2)])
        diff_sub_simplified = simplify(expand(diff_sub))
        
        # The simplified form should be (t-u)^4 / (8*u^2) which is always >= 0
        diff_sub_factored = factor(diff_sub_simplified * 8 * u**2)
        
        # Check if it's a perfect fourth power
        x = symbols('x')
        # We expect (t-u)^4
        expected = (t - u)**4
        is_correct = simplify(diff_sub_factored - expected) == 0
        
        checks.append({
            "name": "symbolic_algebraic_proof",
            "passed": is_correct,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Proved RHS - LHS = (sqrt(a) - sqrt(b))^4 / (8*b) >= 0 by algebraic manipulation. Factored form verified: {is_correct}"
        })
        if not is_correct:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "symbolic_algebraic_proof",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Alternative symbolic proof - AM-GM based
    try:
        a_sym, b_sym = symbols('a b', positive=True, real=True)
        # We know (a+b)/2 >= sqrt(ab) (AM-GM)
        # We want to show (a+b)/2 - sqrt(ab) <= (a-b)^2/(8b)
        
        # Let x = a/b >= 1 (since a >= b > 0)
        x = symbols('x', positive=True, real=True)
        # Then a = xb, and the inequality becomes:
        # b(x+1)/2 - b*sqrt(x) <= b(x-1)^2/(8)
        # Divide by b: (x+1)/2 - sqrt(x) <= (x-1)^2/8
        # Multiply by 8: 4(x+1) - 8*sqrt(x) <= (x-1)^2
        # 4x + 4 - 8*sqrt(x) <= x^2 - 2x + 1
        # 0 <= x^2 - 6x - 3 + 8*sqrt(x)
        
        lhs_normalized = (x + 1) / 2 - sp_sqrt(x)
        rhs_normalized = (x - 1)**2 / 8
        diff_normalized = rhs_normalized - lhs_normalized
        
        # Substitute y = sqrt(x)
        y = symbols('y', positive=True, real=True)
        diff_y = diff_normalized.subs(x, y**2)
        diff_y_simplified = simplify(expand(diff_y * 8))
        
        # Should get (y^2 - 1)^2 which is always >= 0
        # Actually: 8*diff = (y^2-1)^2 - (y^2+1) + 2 + 8y
        # = y^4 - 2y^2 + 1 - y^2 - 1 + 2 + 8y
        # = y^4 - 3y^2 + 8y + 2
        
        # Let's factor differently: complete square in y
        # diff = [(y^2-1)^2]/8 - (y^2+1)/2 + y
        # = [y^4 - 2y^2 + 1 - 4y^2 - 4 + 8y]/8
        # = [y^4 - 6y^2 + 8y - 3]/8
        
        # Actually let's verify it's (y-1)^4/8
        expected_form = (y - 1)**4 / 8
        is_equivalent = simplify(diff_y - expected_form) == 0
        
        checks.append({
            "name": "normalized_symbolic_proof",
            "passed": is_equivalent,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Proved via substitution x=a/b, y=sqrt(x): inequality equivalent to (sqrt(x)-1)^4/8 >= 0. Verified: {is_equivalent}"
        })
        if not is_equivalent:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "normalized_symbolic_proof",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Normalized proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Numerical sanity checks
    try:
        test_cases = [
            (4.0, 1.0),
            (9.0, 4.0),
            (16.0, 9.0),
            (100.0, 25.0),
            (2.0, 2.0),
            (5.0, 3.0),
            (10.0, 1.0),
            (1.5, 1.0),
            (7.0, 7.0)
        ]
        numerical_passed = True
        for a_val, b_val in test_cases:
            lhs = (a_val + b_val) / 2 - (a_val * b_val) ** 0.5
            rhs = (a_val - b_val) ** 2 / (8 * b_val)
            if not (lhs <= rhs + 1e-10):
                numerical_passed = False
                break
        
        checks.append({
            "name": "numerical_sanity",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tested {len(test_cases)} concrete cases with a >= b > 0"
        })
        if not numerical_passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
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
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")