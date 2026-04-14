import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, simplify, nsimplify, N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic solution with SymPy
    check1 = {"name": "symbolic_solution", "backend": "sympy", "proof_type": "symbolic_zero", "passed": False, "details": ""}
    try:
        x_sym, y_sym = symbols('x y', real=True)
        eq1 = 1/x_sym + 1/y_sym - 5
        eq2 = 3*x_sym*y_sym + x_sym + y_sym - 4
        solutions = solve([eq1, eq2], [x_sym, y_sym])
        
        if solutions:
            result_values = []
            for sol in solutions:
                x_val, y_val = sol
                result = x_val**2 * y_val + x_val * y_val**2
                result_simplified = simplify(result)
                result_values.append(result_simplified)
            
            unique_results = list(set(result_values))
            
            if len(unique_results) == 1 and simplify(unique_results[0] - 5/4) == 0:
                check1["passed"] = True
                check1["details"] = f"SymPy solved system and computed x^2*y + x*y^2 = {unique_results[0]} = 5/4. Solutions: {solutions}"
            else:
                check1["details"] = f"SymPy gave inconsistent or wrong results: {unique_results}"
        else:
            check1["details"] = "SymPy found no solutions"
    except Exception as e:
        check1["details"] = f"SymPy symbolic check failed: {str(e)}"
    
    checks.append(check1)
    all_passed = all_passed and check1["passed"]
    
    # Check 2: Algebraic verification with kdrag
    check2 = {"name": "kdrag_algebraic_proof", "backend": "kdrag", "proof_type": "certificate", "passed": False, "details": ""}
    try:
        x = Real("x")
        y = Real("y")
        
        # Given constraints
        constraint1 = (1/x + 1/y == 5)
        constraint2 = (3*x*y + x + y == 4)
        
        # First equation implies x + y = 5*x*y
        lemma1 = kd.prove(ForAll([x, y], 
            Implies(And(x != 0, y != 0, 1/x + 1/y == 5),
                   (x + y)/(x*y) == 5)))
        
        # This means x + y = 5*x*y
        lemma2 = kd.prove(ForAll([x, y],
            Implies(And(x != 0, y != 0, (x + y)/(x*y) == 5),
                   x + y == 5*x*y)))
        
        # Substituting into second equation: 3*x*y + 5*x*y = 4
        lemma3 = kd.prove(ForAll([x, y],
            Implies(And(x + y == 5*x*y, 3*x*y + x + y == 4),
                   8*x*y == 4)))
        
        # Therefore x*y = 1/2
        lemma4 = kd.prove(ForAll([x, y],
            Implies(8*x*y == 4, x*y == 0.5)))
        
        # And x + y = 5/2
        lemma5 = kd.prove(ForAll([x, y],
            Implies(And(x*y == 0.5, x + y == 5*x*y),
                   x + y == 2.5)))
        
        # Finally: x^2*y + x*y^2 = x*y*(x + y) = 0.5 * 2.5 = 1.25
        lemma6 = kd.prove(ForAll([x, y],
            Implies(And(x*y == 0.5, x + y == 2.5),
                   x*x*y + x*y*y == 1.25)))
        
        check2["passed"] = True
        check2["details"] = "kdrag proved all algebraic steps: (1) x+y=5xy, (2) 8xy=4, (3) xy=1/2, (4) x+y=5/2, (5) x^2*y+xy^2=5/4"
    except Exception as e:
        check2["details"] = f"kdrag proof failed: {str(e)}"
    
    checks.append(check2)
    all_passed = all_passed and check2["passed"]
    
    # Check 3: Numerical verification
    check3 = {"name": "numerical_verification", "backend": "numerical", "proof_type": "numerical", "passed": False, "details": ""}
    try:
        from sympy import symbols, solve, N
        x_sym, y_sym = symbols('x y', real=True)
        eq1 = 1/x_sym + 1/y_sym - 5
        eq2 = 3*x_sym*y_sym + x_sym + y_sym - 4
        solutions = solve([eq1, eq2], [x_sym, y_sym])
        
        numerical_results = []
        for sol in solutions:
            x_val, y_val = sol
            result = N(x_val**2 * y_val + x_val * y_val**2, 15)
            numerical_results.append(float(result))
            
            # Verify constraints
            check_eq1 = abs(float(N(1/x_val + 1/y_val, 15)) - 5.0) < 1e-10
            check_eq2 = abs(float(N(3*x_val*y_val + x_val + y_val, 15)) - 4.0) < 1e-10
            
            if check_eq1 and check_eq2:
                diff = abs(float(result) - 1.25)
                if diff < 1e-10:
                    check3["passed"] = True
        
        if check3["passed"]:
            check3["details"] = f"Numerical evaluation gives x^2*y + x*y^2 = {numerical_results[0]:.10f} ≈ 1.25 = 5/4"
        else:
            check3["details"] = f"Numerical results don't match expected 5/4: {numerical_results}"
    except Exception as e:
        check3["details"] = f"Numerical check failed: {str(e)}"
    
    checks.append(check3)
    all_passed = all_passed and check3["passed"]
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Verification result: {result['proved']}")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}): {check['details']}")