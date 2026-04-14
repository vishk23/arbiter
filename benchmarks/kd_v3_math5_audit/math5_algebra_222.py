import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, simplify, Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Z3 proof that x=5 satisfies the equation
    try:
        x = Real("x")
        equation = (16 + 4*x) * (12 - x) == (16 + x) * 12
        constraint = And(equation, x != 0)
        solution_check = Implies(constraint, x == 5)
        
        # Z3 can verify that if the equation holds and x != 0, then x = 5
        # We'll prove the forward direction: x=5 satisfies the equation
        x_val = Real("x_val")
        eq_at_5 = (16 + 4*5) * (12 - 5) == (16 + 5) * 12
        proof = kd.prove(eq_at_5)
        
        checks.append({
            "name": "z3_solution_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved that x=5 satisfies the equation: (16+4*5)*(12-5) = (16+5)*12, yielding 36*7 = 21*12 = 252. Proof: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": "z3_solution_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Z3 proof that the expanded equation holds
    try:
        x = Real("x")
        # Original: (16+4x)(12-x) = (16+x)*12
        # Expanded: 192 - 16x + 48x - 4x^2 = 192 + 12x
        # Simplified: -4x^2 + 32x = 12x
        # Further: -4x^2 + 20x = 0
        # Factor: 4x(5 - x) = 0
        
        lhs = (16 + 4*x) * (12 - x)
        rhs = (16 + x) * 12
        expanded_lhs = 192 - 16*x + 48*x - 4*x*x
        expanded_rhs = 192 + 12*x
        
        expansion_correct = (lhs == rhs) == (expanded_lhs == expanded_rhs)
        proof = kd.prove(ForAll([x], expansion_correct))
        
        checks.append({
            "name": "z3_expansion_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved the algebraic expansion is correct. Proof: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": "z3_expansion_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 expansion proof failed: {str(e)}"
        })
        all_passed = False
    
    # Check 3: SymPy symbolic verification
    try:
        x_sym = symbols('x', real=True)
        equation = (16 + 4*x_sym) * (12 - x_sym) - (16 + x_sym) * 12
        expanded = simplify(equation)
        
        # Should simplify to -4x^2 + 20x = 4x(5-x)
        solutions = solve(equation, x_sym)
        
        # Filter out x=0 since problem states x != 0
        non_zero_solutions = [sol for sol in solutions if sol != 0]
        
        passed = len(non_zero_solutions) == 1 and non_zero_solutions[0] == 5
        
        checks.append({
            "name": "sympy_solution",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy found solutions: {solutions}. Non-zero solution: {non_zero_solutions}. Expanded form: {expanded}"
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical verification at x=5
    try:
        x_val = 5
        denali_scenario1 = 16 + 4*x_val  # 36 dogs
        nate_scenario1 = 12  # 12 dogs
        ratio1 = denali_scenario1 / nate_scenario1
        
        denali_scenario2 = 16 + x_val  # 21 dogs
        nate_scenario2 = 12 - x_val  # 7 dogs
        ratio2 = denali_scenario2 / nate_scenario2
        
        ratios_equal = abs(ratio1 - ratio2) < 1e-10
        
        checks.append({
            "name": "numerical_verification",
            "passed": ratios_equal,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x=5: Scenario 1 ratio = {ratio1} (36/12), Scenario 2 ratio = {ratio2} (21/7). Equal: {ratios_equal}"
        })
        
        if not ratios_equal:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical verification failed: {str(e)}"
        })
        all_passed = False
    
    # Check 5: Z3 proof that x=0 does NOT satisfy the non-triviality requirement
    try:
        x = Real("x")
        # At x=0, both scenarios give 16/12, so equation holds but violates x != 0
        at_zero = And((16 + 4*0) * (12 - 0) == (16 + 0) * 12, 0 != 0)
        proof = kd.prove(Not(at_zero))
        
        checks.append({
            "name": "z3_exclude_zero",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 proved that x=0 is excluded by the constraint x != 0. Proof: {proof}"
        })
    except Exception as e:
        checks.append({
            "name": "z3_exclude_zero",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 zero exclusion proof failed: {str(e)}"
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
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")