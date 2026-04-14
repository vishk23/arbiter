import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, Poly

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic expansion verification using SymPy
    try:
        x = symbols('x')
        f_expr = x**7 - 3*x**3 + 2
        g_expr = f_expr.subs(x, x + 1)
        g_expanded = expand(g_expr)
        
        # Get coefficients
        g_poly = Poly(g_expanded, x)
        coeffs = g_poly.all_coeffs()
        symbolic_sum = sum(coeffs)
        
        # Verify sum equals 106
        check_symbolic = (symbolic_sum == 106)
        
        checks.append({
            "name": "symbolic_expansion",
            "passed": check_symbolic,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Expanded g(x) = f(x+1) symbolically. Coefficient sum: {symbolic_sum}. Expected: 106. Match: {check_symbolic}"
        })
        all_passed = all_passed and check_symbolic
    except Exception as e:
        checks.append({
            "name": "symbolic_expansion",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify g(1) = f(2) using kdrag
    try:
        x = Real('x')
        f = lambda t: t**7 - 3*t**3 + 2
        
        # f(2) = 2^7 - 3*2^3 + 2 = 128 - 24 + 2 = 106
        f_at_2 = f(2.0)
        
        # For g(x) = f(x+1), g(1) = f(1+1) = f(2)
        g_at_1 = f(1.0 + 1.0)
        
        # Verify f(2) = 106
        thm = kd.prove(f(2.0) == 106.0)
        
        checks.append({
            "name": "kdrag_f_at_2",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(2) = 106 using Z3. Certificate: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_f_at_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(2) = 106: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_f_at_2",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify the algebraic identity g(1) - 106 = 0 using SymPy minimal polynomial
    try:
        x_sym = symbols('x')
        f_expr = x_sym**7 - 3*x_sym**3 + 2
        g_at_1_expr = f_expr.subs(x_sym, 2)
        
        # Compute g(1) - 106
        diff = g_at_1_expr - 106
        
        # Simplify
        from sympy import simplify
        diff_simplified = simplify(diff)
        
        # Verify it's exactly zero
        is_zero = (diff_simplified == 0)
        
        checks.append({
            "name": "sympy_algebraic_zero",
            "passed": is_zero,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified g(1) - 106 = {diff_simplified} (should be 0). Is zero: {is_zero}"
        })
        all_passed = all_passed and is_zero
    except Exception as e:
        checks.append({
            "name": "sympy_algebraic_zero",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical sanity check
    try:
        # Direct computation
        f_2_numerical = 2**7 - 3*(2**3) + 2
        passed = (f_2_numerical == 106)
        
        checks.append({
            "name": "numerical_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"f(2) computed numerically: {f_2_numerical}. Expected: 106. Match: {passed}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Verify coefficient sum property using kdrag on integers
    try:
        # For polynomial g with integer coefficients, sum of coefficients = g(1)
        # We've shown g(1) = f(2) = 106
        # This is the key theorem
        
        x_int = Int('x')
        # Define f symbolically for integers
        f_int = lambda t: t**7 - 3*t**3 + 2
        
        # Prove f(2) = 106 for integers
        thm_int = kd.prove(f_int(2) == 106)
        
        checks.append({
            "name": "kdrag_integer_computation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(2) = 106 over integers. Certificate: {thm_int}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_integer_computation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_integer_computation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
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
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"    {check['details']}")