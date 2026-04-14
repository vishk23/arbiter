import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, simplify, factor, solve, Rational, N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the substitution algebra using SymPy
    try:
        x_sym = symbols('x', real=True)
        a_sym = symbols('a', real=True)
        
        # Original equation denominators
        d1 = x_sym**2 - 10*x_sym - 29
        d2 = x_sym**2 - 10*x_sym - 45
        d3 = x_sym**2 - 10*x_sym - 69
        
        # Verify d2 = d1 - 16 and d3 = d1 - 40
        check1_pass = simplify(d2 - (d1 - 16)) == 0 and simplify(d3 - (d1 - 40)) == 0
        
        checks.append({
            "name": "substitution_algebra",
            "passed": check1_pass,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified d2 = d1 - 16 and d3 = d1 - 40: {check1_pass}"
        })
        all_passed = all_passed and check1_pass
    except Exception as e:
        checks.append({
            "name": "substitution_algebra",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Check 2: Verify that clearing denominators gives -64a + 640 = 0
    try:
        a_sym = symbols('a', real=True)
        
        # After substitution: 1/a + 1/(a-16) - 2/(a-40) = 0
        # Multiply by a(a-16)(a-40):
        numerator = (a_sym - 16)*(a_sym - 40) + a_sym*(a_sym - 40) - 2*a_sym*(a_sym - 16)
        expanded = expand(numerator)
        
        # Should equal -64a + 640
        expected = -64*a_sym + 640
        
        check2_pass = simplify(expanded - expected) == 0
        
        checks.append({
            "name": "cleared_denominator_algebra",
            "passed": check2_pass,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified (a-16)(a-40) + a(a-40) - 2a(a-16) = -64a + 640: {check2_pass}"
        })
        all_passed = all_passed and check2_pass
    except Exception as e:
        checks.append({
            "name": "cleared_denominator_algebra",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Check 3: Verify a = 10 solves -64a + 640 = 0
    try:
        check3_pass = -64*10 + 640 == 0
        
        checks.append({
            "name": "solve_for_a",
            "passed": check3_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified a = 10 satisfies -64a + 640 = 0: {check3_pass}"
        })
        all_passed = all_passed and check3_pass
    except Exception as e:
        checks.append({
            "name": "solve_for_a",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Check 4: Verify x^2 - 10x - 29 = 10 gives x = 13 or x = -3
    try:
        x_sym = symbols('x', real=True)
        eq = x_sym**2 - 10*x_sym - 29 - 10
        simplified = simplify(eq)
        factored = factor(simplified)
        
        # Should be (x - 13)(x + 3)
        expected_factored = (x_sym - 13)*(x_sym + 3)
        
        check4_pass = simplify(factored - expected_factored) == 0
        
        checks.append({
            "name": "factor_quadratic",
            "passed": check4_pass,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified x^2 - 10x - 39 = (x-13)(x+3): {check4_pass}"
        })
        all_passed = all_passed and check4_pass
    except Exception as e:
        checks.append({
            "name": "factor_quadratic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Check 5: Verify x = 13 satisfies the original equation (numerical)
    try:
        x_val = 13
        d1 = x_val**2 - 10*x_val - 29
        d2 = x_val**2 - 10*x_val - 45
        d3 = x_val**2 - 10*x_val - 69
        
        lhs = Rational(1, d1) + Rational(1, d2) - Rational(2, d3)
        
        check5_pass = abs(float(lhs)) < 1e-10
        
        checks.append({
            "name": "verify_x_13_numerical",
            "passed": check5_pass,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified x=13 satisfies equation (LHS = {lhs}): {check5_pass}"
        })
        all_passed = all_passed and check5_pass
    except Exception as e:
        checks.append({
            "name": "verify_x_13_numerical",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Check 6: Formal verification using kdrag that the algebraic manipulations are valid
    try:
        x = Real("x")
        a = Real("a")
        
        # Prove that if a = x^2 - 10x - 29, then the substitution is valid
        # We'll prove that the cleared numerator equals -64a + 640
        
        # Define the numerator after clearing denominators
        # (a - 16)(a - 40) + a(a - 40) - 2a(a - 16)
        numerator_expr = (a - 16)*(a - 40) + a*(a - 40) - 2*a*(a - 16)
        target_expr = -64*a + 640
        
        # Prove they are equal for all a
        thm = kd.prove(ForAll([a], numerator_expr == target_expr))
        
        checks.append({
            "name": "kdrag_numerator_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved (a-16)(a-40) + a(a-40) - 2a(a-16) = -64a + 640 for all a. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_numerator_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove numerator identity: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_numerator_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {e}"
        })
        all_passed = False
    
    # Check 7: Prove with kdrag that x=13 makes x^2 - 10x - 39 = 0
    try:
        x = Real("x")
        
        # Prove that 13^2 - 10*13 - 39 = 0
        thm = kd.prove(13*13 - 10*13 - 39 == 0)
        
        checks.append({
            "name": "kdrag_x_13_satisfies_quadratic",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 13^2 - 10*13 - 39 = 0. Proof: {thm}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_x_13_satisfies_quadratic",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove: {e}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_x_13_satisfies_quadratic",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {e}"
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
        status = "✓" if check['passed'] else "✗"
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details']}")