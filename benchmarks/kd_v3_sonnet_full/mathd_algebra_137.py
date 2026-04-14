import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, Implies, And
from sympy import symbols, Eq, solve, N

def verify():
    checks = []
    all_passed = True
    
    # CHECK 1: Symbolic solution with SymPy
    try:
        x = symbols('x', real=True, positive=True)
        equation = Eq(x * 1.04, 598)
        solution = solve(equation, x)
        
        if solution and len(solution) == 1:
            sol_value = solution[0]
            is_575 = abs(sol_value - 575) < 1e-10
            
            checks.append({
                "name": "sympy_symbolic_solution",
                "passed": is_575,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Solved x * 1.04 = 598 symbolically. Solution: {sol_value}. Is 575: {is_575}"
            })
            all_passed = all_passed and is_575
        else:
            checks.append({
                "name": "sympy_symbolic_solution",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Unexpected solution count: {len(solution) if solution else 0}"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solving failed: {str(e)}"
        })
        all_passed = False
    
    # CHECK 2: kdrag formal verification
    try:
        last_year = Real('last_year')
        this_year = Real('this_year')
        
        # Define the relationship: this_year = last_year * 1.04
        relationship = ForAll([last_year, this_year],
            Implies(
                And(this_year == last_year * 1.04, this_year == 598),
                last_year == 575
            )
        )
        
        proof = kd.prove(relationship)
        
        checks.append({
            "name": "kdrag_formal_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proved: ForAll last_year, this_year. (this_year = last_year * 1.04 AND this_year = 598) => last_year = 575. Proof object: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_formal_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed (LemmaError): {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_formal_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed (unexpected error): {str(e)}"
        })
        all_passed = False
    
    # CHECK 3: Numerical verification (forward)
    try:
        last_year_val = 575
        computed_this_year = last_year_val * 1.04
        forward_check = abs(computed_this_year - 598) < 1e-10
        
        checks.append({
            "name": "numerical_forward_check",
            "passed": forward_check,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Forward check: 575 * 1.04 = {computed_this_year}. Expected 598. Difference: {abs(computed_this_year - 598)}"
        })
        all_passed = all_passed and forward_check
    except Exception as e:
        checks.append({
            "name": "numerical_forward_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical forward check failed: {str(e)}"
        })
        all_passed = False
    
    # CHECK 4: Numerical verification (backward)
    try:
        this_year_val = 598
        computed_last_year = this_year_val / 1.04
        backward_check = abs(computed_last_year - 575) < 1e-10
        
        checks.append({
            "name": "numerical_backward_check",
            "passed": backward_check,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Backward check: 598 / 1.04 = {computed_last_year}. Expected 575. Difference: {abs(computed_last_year - 575)}"
        })
        all_passed = all_passed and backward_check
    except Exception as e:
        checks.append({
            "name": "numerical_backward_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical backward check failed: {str(e)}"
        })
        all_passed = False
    
    # CHECK 5: Alternative equation form x + 0.04x = 598
    try:
        x = symbols('x', real=True, positive=True)
        alt_equation = Eq(x + 0.04*x, 598)
        alt_solution = solve(alt_equation, x)
        
        if alt_solution and len(alt_solution) == 1:
            alt_sol_value = alt_solution[0]
            alt_is_575 = abs(alt_sol_value - 575) < 1e-10
            
            checks.append({
                "name": "sympy_alternative_form",
                "passed": alt_is_575,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Solved x + 0.04x = 598 symbolically. Solution: {alt_sol_value}. Is 575: {alt_is_575}"
            })
            all_passed = all_passed and alt_is_575
        else:
            checks.append({
                "name": "sympy_alternative_form",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Unexpected solution count: {len(alt_solution) if alt_solution else 0}"
            })
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_alternative_form",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy alternative form solving failed: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")