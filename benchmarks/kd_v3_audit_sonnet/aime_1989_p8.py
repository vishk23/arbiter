import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Eq
from sympy import symbols, solve, Rational

def verify():
    checks = []
    all_passed = True
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 1: Verify the linear system for a, b, c using kdrag
    # ═══════════════════════════════════════════════════════════════
    try:
        a_var = Real('a_var')
        b_var = Real('b_var')
        c_var = Real('c_var')
        
        # System constraints from f(1)=1, f(2)=12, f(3)=123
        constraint1 = (a_var + b_var + c_var == 1)
        constraint2 = (4*a_var + 2*b_var + c_var == 12)
        constraint3 = (9*a_var + 3*b_var + c_var == 123)
        
        # The unique solution
        solution_constraint = And(a_var == 50, b_var == -139, c_var == 90)
        
        # Prove that the solution satisfies all constraints
        thm = kd.prove(
            Implies(
                solution_constraint,
                And(constraint1, constraint2, constraint3)
            )
        )
        
        checks.append({
            "name": "linear_system_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved a=50, b=-139, c=90 satisfies the system: {thm}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "linear_system_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove system solution: {e}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 2: Verify f(4) = 334 using kdrag
    # ═══════════════════════════════════════════════════════════════
    try:
        a_var = Real('a_var2')
        b_var = Real('b_var2')
        c_var = Real('c_var2')
        
        # If a=50, b=-139, c=90, then f(4) = 16a + 4b + c = 334
        thm2 = kd.prove(
            Implies(
                And(a_var == 50, b_var == -139, c_var == 90),
                16*a_var + 4*b_var + c_var == 334
            )
        )
        
        checks.append({
            "name": "f4_equals_334",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved f(4) = 16*50 + 4*(-139) + 90 = 334: {thm2}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "f4_equals_334",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(4)=334: {e}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 3: Symbolic verification using SymPy
    # ═══════════════════════════════════════════════════════════════
    try:
        a, b, c = symbols('a b c')
        
        # System of equations
        eq1 = a + b + c - 1
        eq2 = 4*a + 2*b + c - 12
        eq3 = 9*a + 3*b + c - 123
        
        # Solve the system
        solution = solve([eq1, eq2, eq3], [a, b, c])
        
        # Verify solution
        a_sol = solution[a]
        b_sol = solution[b]
        c_sol = solution[c]
        
        # Compute f(4)
        f4 = 16*a_sol + 4*b_sol + c_sol
        
        passed = (a_sol == 50 and b_sol == -139 and c_sol == 90 and f4 == 334)
        
        if not passed:
            all_passed = False
        
        checks.append({
            "name": "sympy_symbolic_solve",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solution: a={a_sol}, b={b_sol}, c={c_sol}, f(4)={f4}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "sympy_symbolic_solve",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve failed: {e}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 4: Numerical sanity check
    # ═══════════════════════════════════════════════════════════════
    try:
        a_num = 50
        b_num = -139
        c_num = 90
        
        # Verify the system
        f1 = a_num + b_num + c_num
        f2 = 4*a_num + 2*b_num + c_num
        f3 = 9*a_num + 3*b_num + c_num
        f4_num = 16*a_num + 4*b_num + c_num
        
        passed = (abs(f1 - 1) < 1e-10 and 
                  abs(f2 - 12) < 1e-10 and 
                  abs(f3 - 123) < 1e-10 and 
                  abs(f4_num - 334) < 1e-10)
        
        if not passed:
            all_passed = False
        
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check: f(1)={f1}, f(2)={f2}, f(3)={f3}, f(4)={f4_num}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
    
    # ═══════════════════════════════════════════════════════════════
    # CHECK 5: Verify uniqueness of solution using kdrag
    # ═══════════════════════════════════════════════════════════════
    try:
        a1 = Real('a1')
        b1 = Real('b1')
        c1 = Real('c1')
        
        # The system uniquely determines a, b, c
        system = And(
            a1 + b1 + c1 == 1,
            4*a1 + 2*b1 + c1 == 12,
            9*a1 + 3*b1 + c1 == 123
        )
        
        # If the system holds, then a=50, b=-139, c=90
        thm3 = kd.prove(
            Implies(
                system,
                And(a1 == 50, b1 == -139, c1 == 90)
            )
        )
        
        checks.append({
            "name": "uniqueness_of_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved uniqueness of a=50, b=-139, c=90: {thm3}"
        })
    except Exception as e:
        all_passed = False
        checks.append({
            "name": "uniqueness_of_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove uniqueness: {e}"
        })
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}/{check['proof_type']}): {check['details'][:100]}")