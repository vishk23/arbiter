import kdrag as kd
from kdrag.smt import *
from sympy import symbols, solve, N

def verify():
    checks = []
    all_passed = True

    # Check 1: Kdrag formal proof of the linear system
    try:
        x, y, z = Reals("x y z")
        eq1 = (3*x + y == 17)
        eq2 = (5*y + z == 14)
        eq3 = (3*x + 5*z == 41)
        system = And(eq1, eq2, eq3)
        
        # Prove that the system implies x+y+z=12
        claim = ForAll([x, y, z], Implies(system, x + y + z == 12))
        proof = kd.prove(claim)
        
        checks.append({
            "name": "kdrag_linear_system_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Formally proved that system (3x+y=17, 5y+z=14, 3x+5z=41) implies x+y+z=12. Proof object: {proof}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "kdrag_linear_system_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove with kdrag: {e}"
        })

    # Check 2: SymPy symbolic solution
    try:
        x_s, y_s, z_s = symbols('x y z', real=True)
        eq1_s = 3*x_s + y_s - 17
        eq2_s = 5*y_s + z_s - 14
        eq3_s = 3*x_s + 5*z_s - 41
        
        solution = solve([eq1_s, eq2_s, eq3_s], [x_s, y_s, z_s])
        
        if solution:
            sum_val = solution[x_s] + solution[y_s] + solution[z_s]
            is_twelve = (sum_val == 12)
            
            checks.append({
                "name": "sympy_symbolic_solution",
                "passed": is_twelve,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solution: x={solution[x_s]}, y={solution[y_s]}, z={solution[z_s]}, sum={sum_val}, equals_12={is_twelve}"
            })
            
            if not is_twelve:
                all_passed = False
        else:
            all_passed = False
            checks.append({
                "name": "sympy_symbolic_solution",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": "No solution found by SymPy"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_symbolic_solution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy error: {e}"
        })

    # Check 3: Numerical verification with concrete values
    try:
        x_s, y_s, z_s = symbols('x y z', real=True)
        solution = solve([3*x_s + y_s - 17, 5*y_s + z_s - 14, 3*x_s + 5*z_s - 41], [x_s, y_s, z_s])
        
        if solution:
            x_val = float(N(solution[x_s], 50))
            y_val = float(N(solution[y_s], 50))
            z_val = float(N(solution[z_s], 50))
            
            # Verify equations
            eq1_check = abs(3*x_val + y_val - 17) < 1e-10
            eq2_check = abs(5*y_val + z_val - 14) < 1e-10
            eq3_check = abs(3*x_val + 5*z_val - 41) < 1e-10
            sum_check = abs(x_val + y_val + z_val - 12) < 1e-10
            
            passed = eq1_check and eq2_check and eq3_check and sum_check
            
            checks.append({
                "name": "numerical_verification",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"x={x_val:.10f}, y={y_val:.10f}, z={z_val:.10f}, sum={x_val+y_val+z_val:.10f}, eq1={eq1_check}, eq2={eq2_check}, eq3={eq3_check}, sum_is_12={sum_check}"
            })
            
            if not passed:
                all_passed = False
        else:
            all_passed = False
            checks.append({
                "name": "numerical_verification",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "No solution to verify"
            })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical error: {e}"
        })

    # Check 4: Verify hint (sum equations)
    try:
        passed = (17 + 14 + 41 == 72) and (72 / 6 == 12)
        checks.append({
            "name": "hint_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Hint: (3x+y)+(5y+z)+(3x+5z)=17+14+41=72, 6x+6y+6z=72, x+y+z=12. Arithmetic check: {passed}"
        })
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "hint_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {e}"
        })

    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        print(f"\nCheck: {check['name']}")
        print(f"  Passed: {check['passed']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Proof type: {check['proof_type']}")
        print(f"  Details: {check['details']}")