import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Or
from sympy import Symbol, solve, simplify, N, Rational
from sympy.polys import minimal_polynomial

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify x=13 satisfies the original equation using SymPy
    try:
        x_sym = Symbol('x')
        original_eq = 1/(x_sym**2 - 10*x_sym - 29) + 1/(x_sym**2 - 10*x_sym - 45) - 2/(x_sym**2 - 10*x_sym - 69)
        
        # Substitute x=13
        result_at_13 = original_eq.subs(x_sym, 13)
        result_simplified = simplify(result_at_13)
        
        # Verify it equals zero symbolically
        is_zero = (result_simplified == 0)
        
        # Also check minimal polynomial for rigor
        mp = minimal_polynomial(result_simplified, Symbol('t'))
        mp_is_t = (mp == Symbol('t'))
        
        checks.append({
            "name": "x=13_satisfies_equation_symbolic",
            "passed": is_zero and mp_is_t,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Substituted x=13 into original equation, got {result_simplified}, minimal_polynomial={mp}"
        })
        all_passed = all_passed and is_zero and mp_is_t
    except Exception as e:
        checks.append({
            "name": "x=13_satisfies_equation_symbolic",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify the substitution approach algebraically
    try:
        x_sym = Symbol('x')
        a = Symbol('a')
        
        # Define a = x^2 - 10x - 29
        # Then x^2 - 10x - 45 = a - 16
        # And x^2 - 10x - 69 = a - 40
        
        # The equation becomes: 1/a + 1/(a-16) - 2/(a-40) = 0
        substituted_eq = 1/a + 1/(a - 16) - 2/(a - 40)
        
        # Clear denominators: (a-16)(a-40) + a(a-40) - 2*a*(a-16) = 0
        cleared = simplify(substituted_eq * a * (a - 16) * (a - 40))
        
        # Solve for a
        a_solutions = solve(cleared, a)
        
        # We expect a = 10
        has_a_10 = 10 in a_solutions
        
        # Now solve x^2 - 10x - 29 = 10 => x^2 - 10x - 39 = 0
        x_from_a_10 = solve(x_sym**2 - 10*x_sym - 29 - 10, x_sym)
        
        # We expect x = 13 or x = -3
        has_x_13 = 13 in x_from_a_10
        has_x_neg3 = -3 in x_from_a_10
        
        checks.append({
            "name": "substitution_method_verification",
            "passed": has_a_10 and has_x_13 and has_x_neg3,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Found a={a_solutions}, x from a=10 gives {x_from_a_10}, positive solution is 13"
        })
        all_passed = all_passed and has_a_10 and has_x_13 and has_x_neg3
    except Exception as e:
        checks.append({
            "name": "substitution_method_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify x=13 is positive and x=-3 is not
    try:
        x_sym = Symbol('x')
        x_solutions = solve(x_sym**2 - 10*x_sym - 39, x_sym)
        
        positive_solutions = [sol for sol in x_solutions if sol > 0]
        
        is_13_only_positive = (positive_solutions == [13])
        
        checks.append({
            "name": "positive_solution_uniqueness",
            "passed": is_13_only_positive,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"All solutions: {x_solutions}, positive solutions: {positive_solutions}"
        })
        all_passed = all_passed and is_13_only_positive
    except Exception as e:
        checks.append({
            "name": "positive_solution_uniqueness",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical sanity check
    try:
        x_val = 13
        denom1 = x_val**2 - 10*x_val - 29
        denom2 = x_val**2 - 10*x_val - 45
        denom3 = x_val**2 - 10*x_val - 69
        
        result = 1/denom1 + 1/denom2 - 2/denom3
        
        # Check if result is very close to 0 (numerical tolerance)
        is_close_to_zero = abs(result) < 1e-10
        
        checks.append({
            "name": "numerical_verification_x13",
            "passed": is_close_to_zero,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Evaluated at x=13: result={result}, |result|={abs(result)}"
        })
        all_passed = all_passed and is_close_to_zero
    except Exception as e:
        checks.append({
            "name": "numerical_verification_x13",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Verify using kdrag that x=13 satisfies the quadratic from substitution
    try:
        x = Real("x")
        # From a=10 and a = x^2 - 10x - 29, we get x^2 - 10x - 39 = 0
        # This factors as (x-13)(x+3) = 0
        
        # Prove that if x^2 - 10x - 39 = 0 and x > 0, then x = 13
        claim = ForAll([x], Implies(And(x*x - 10*x - 39 == 0, x > 0), x == 13))
        
        proof = kd.prove(claim)
        
        checks.append({
            "name": "kdrag_quadratic_positive_root",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that x^2-10x-39=0 and x>0 implies x=13: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_quadratic_positive_root",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"LemmaError: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_quadratic_positive_root",
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
        status = "PASS" if check['passed'] else "FAIL"
        print(f"  [{status}] {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"      {check['details']}")