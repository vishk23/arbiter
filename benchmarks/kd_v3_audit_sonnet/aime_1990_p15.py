import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, And, Implies
from sympy import symbols, solve, Rational, N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Symbolic solution using SymPy
    try:
        a_sym, b_sym, x_sym, y_sym = symbols('a b x y', real=True)
        
        eq1 = a_sym*x_sym + b_sym*y_sym - 3
        eq2 = a_sym*x_sym**2 + b_sym*y_sym**2 - 7
        eq3 = a_sym*x_sym**3 + b_sym*y_sym**3 - 16
        eq4 = a_sym*x_sym**4 + b_sym*y_sym**4 - 42
        
        solutions = solve([eq1, eq2, eq3, eq4], [a_sym, b_sym, x_sym, y_sym], dict=True)
        
        symbolic_passed = False
        symbolic_details = ""
        
        if solutions:
            for sol in solutions:
                if all(k in sol for k in [a_sym, b_sym, x_sym, y_sym]):
                    a_val = sol[a_sym]
                    b_val = sol[b_sym]
                    x_val = sol[x_sym]
                    y_val = sol[y_sym]
                    
                    result = a_val * x_val**5 + b_val * y_val**5
                    
                    # Check if result simplifies to 20
                    from sympy import simplify
                    result_simplified = simplify(result)
                    
                    if result_simplified == 20 or abs(float(result_simplified) - 20) < 1e-6:
                        symbolic_passed = True
                        symbolic_details = f"Found solution: ax^5 + by^5 = {result_simplified}"
                        break
            
            if not symbolic_passed:
                symbolic_details = "Solutions found but ax^5 + by^5 != 20"
        else:
            symbolic_details = "No symbolic solutions found"
        
        checks.append({
            "name": "symbolic_solution",
            "passed": symbolic_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": symbolic_details
        })
        
        if not symbolic_passed:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "symbolic_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error in symbolic solution: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Verify recurrence relation using kdrag
    try:
        S, P = Real('S'), Real('P')
        s1, s2, s3, s4, s5 = Real('s1'), Real('s2'), Real('s3'), Real('s4'), Real('s5')
        
        # Define the recurrence: s_n * S = s_{n+1} + P * s_{n-1}
        recurrence_holds = And(
            s1 == 3,
            s2 == 7,
            s3 == 16,
            s4 == 42,
            s2 * S == s3 + P * s1,
            s3 * S == s4 + P * s2,
            s4 * S == s5 + P * s3
        )
        
        # Prove that if recurrence holds with S=-14, P=-38, then s5=20
        theorem = ForAll([s1, s2, s3, s4, s5, S, P],
            Implies(
                And(
                    recurrence_holds,
                    S == -14,
                    P == -38
                ),
                s5 == 20
            )
        )
        
        proof = kd.prove(theorem)
        
        checks.append({
            "name": "recurrence_verification",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved recurrence relation implies s5 = 20: {proof}"
        })
        
    except Exception as e:
        checks.append({
            "name": "recurrence_verification",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove recurrence: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify S and P values satisfy the system
    try:
        S, P = Real('S'), Real('P')
        
        # From hint: 7S = 16 + 3P and 16S = 42 + 7P
        system_equations = And(
            7*S == 16 + 3*P,
            16*S == 42 + 7*P
        )
        
        # Prove this implies S = -14 and P = -38
        theorem = ForAll([S, P],
            Implies(
                system_equations,
                And(S == -14, P == -38)
            )
        )
        
        proof = kd.prove(theorem)
        
        checks.append({
            "name": "system_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved S=-14, P=-38 from system: {proof}"
        })
        
    except Exception as e:
        checks.append({
            "name": "system_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove system solution: {str(e)}"
        })
        all_passed = False
    
    # Check 4: Numerical verification with concrete example
    try:
        # Use one of the symbolic solutions
        a_sym, b_sym, x_sym, y_sym = symbols('a b x y', real=True)
        
        eq1 = a_sym*x_sym + b_sym*y_sym - 3
        eq2 = a_sym*x_sym**2 + b_sym*y_sym**2 - 7
        eq3 = a_sym*x_sym**3 + b_sym*y_sym**3 - 16
        eq4 = a_sym*x_sym**4 + b_sym*y_sym**4 - 42
        
        solutions = solve([eq1, eq2, eq3, eq4], [a_sym, b_sym, x_sym, y_sym], dict=True)
        
        numerical_passed = False
        numerical_details = ""
        
        if solutions:
            for sol in solutions:
                if all(k in sol for k in [a_sym, b_sym, x_sym, y_sym]):
                    try:
                        a_val = float(N(sol[a_sym], 15))
                        b_val = float(N(sol[b_sym], 15))
                        x_val = float(N(sol[x_sym], 15))
                        y_val = float(N(sol[y_sym], 15))
                        
                        # Verify original equations
                        v1 = a_val*x_val + b_val*y_val
                        v2 = a_val*x_val**2 + b_val*y_val**2
                        v3 = a_val*x_val**3 + b_val*y_val**3
                        v4 = a_val*x_val**4 + b_val*y_val**4
                        
                        if (abs(v1 - 3) < 1e-6 and abs(v2 - 7) < 1e-6 and 
                            abs(v3 - 16) < 1e-6 and abs(v4 - 42) < 1e-6):
                            
                            result = a_val * x_val**5 + b_val * y_val**5
                            
                            if abs(result - 20) < 1e-6:
                                numerical_passed = True
                                numerical_details = f"Numerical verification: a={a_val:.6f}, b={b_val:.6f}, x={x_val:.6f}, y={y_val:.6f}, ax^5+by^5={result:.6f}"
                                break
                    except (ValueError, TypeError):
                        continue
            
            if not numerical_passed:
                numerical_details = "No valid numerical solution verified"
        else:
            numerical_details = "No solutions to verify numerically"
        
        checks.append({
            "name": "numerical_verification",
            "passed": numerical_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": numerical_details
        })
        
        if not numerical_passed:
            all_passed = False
            
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error in numerical verification: {str(e)}"
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
        print(f"\nCheck: {check['name']}")
        print(f"  Passed: {check['passed']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Proof type: {check['proof_type']}")
        print(f"  Details: {check['details']}")