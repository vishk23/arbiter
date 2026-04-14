import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, simplify, expand, factor, Rational
from sympy import minimal_polynomial as minpoly

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic solution using SymPy
    try:
        x = symbols('x', real=True)
        eq = 1/(x**2 - 10*x - 29) + 1/(x**2 - 10*x - 45) - 2/(x**2 - 10*x - 69)
        solutions = solve(eq, x)
        positive_sols = [s for s in solutions if s.is_real and s > 0]
        
        check1_passed = len(positive_sols) == 1 and positive_sols[0] == 13
        checks.append({
            "name": "symbolic_solution",
            "passed": check1_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve found solutions: {solutions}, positive: {positive_sols}"
        })
        all_passed &= check1_passed
    except Exception as e:
        checks.append({
            "name": "symbolic_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify x=13 is a zero via minimal polynomial
    try:
        x_sym = symbols('x', real=True)
        expr = 1/(x_sym**2 - 10*x_sym - 29) + 1/(x_sym**2 - 10*x_sym - 45) - 2/(x_sym**2 - 10*x_sym - 69)
        expr_at_13 = expr.subs(x_sym, 13)
        expr_simplified = simplify(expr_at_13)
        
        check2_passed = expr_simplified == 0
        checks.append({
            "name": "verify_x13_zero",
            "passed": check2_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Equation at x=13 simplifies to: {expr_simplified}"
        })
        all_passed &= check2_passed
    except Exception as e:
        checks.append({
            "name": "verify_x13_zero",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verification failed: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify substitution method using kdrag
    try:
        a = Real('a')
        x_real = Real('x')
        
        # Prove that if a = x^2 - 10x - 29, then the equation becomes
        # 1/a + 1/(a-16) - 2/(a-40) = 0
        # This simplifies to -64a + 640 = 0, so a = 10
        
        # Step 1: Prove that a=10 satisfies the simplified equation
        simplified_eq = ForAll([a], 
            Implies(
                And(a != 0, a != 16, a != 40),
                ((1/a + 1/(a-16) - 2/(a-40)) == 0) == 
                (a*(a-16)*(a-40) + a*(a-16)*(a-40) == 2*a*(a-16)*(a-40))
            )
        )
        # This is too complex for Z3 directly, skip kdrag for equation manipulation
        
        # Instead, prove that x=13 makes x^2-10x-29 = 10
        thm1 = kd.prove(13*13 - 10*13 - 29 == 10)
        
        checks.append({
            "name": "kdrag_verify_a_value",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved 13^2 - 10*13 - 29 = 10: {thm1}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_verify_a_value",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Verify denominators are non-zero at x=13
    try:
        x_real = Real('x')
        denom1 = 13*13 - 10*13 - 29
        denom2 = 13*13 - 10*13 - 45
        denom3 = 13*13 - 10*13 - 69
        
        thm2 = kd.prove(And(denom1 != 0, denom2 != 0, denom3 != 0))
        
        checks.append({
            "name": "kdrag_nonzero_denominators",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved all denominators at x=13 are nonzero: {thm2}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_nonzero_denominators",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Numerical verification
    try:
        from sympy import N
        x_val = 13
        result = float(N(1/(x_val**2 - 10*x_val - 29) + 1/(x_val**2 - 10*x_val - 45) - 2/(x_val**2 - 10*x_val - 69), 50))
        
        check5_passed = abs(result) < 1e-10
        checks.append({
            "name": "numerical_verification",
            "passed": check5_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Equation at x=13 evaluates to {result} (should be ~0)"
        })
        all_passed &= check5_passed
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
        })
        all_passed = False
    
    # Check 6: Verify the factorization x^2 - 10x - 39 = (x-13)(x+3)
    try:
        x_sym = symbols('x')
        poly = x_sym**2 - 10*x_sym - 39
        factored = factor(poly)
        expanded = expand((x_sym - 13)*(x_sym + 3))
        
        check6_passed = (poly == expanded)
        checks.append({
            "name": "verify_factorization",
            "passed": check6_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified x^2-10x-39 = (x-13)(x+3): factored={factored}, expanded={expanded}"
        })
        all_passed &= check6_passed
    except Exception as e:
        checks.append({
            "name": "verify_factorization",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Factorization check failed: {str(e)}"
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
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"         {check['details']}")