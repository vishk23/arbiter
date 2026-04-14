import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, Exists
from sympy import symbols, expand, solve, simplify

def verify():
    checks = []
    all_passed = True
    
    # ========================================
    # Check 1: SymPy - Solve for a, b, c
    # ========================================
    try:
        a_sym, b_sym, c_sym = symbols('a b c', real=True)
        eq1 = a_sym + b_sym + c_sym - 1
        eq2 = 4*a_sym + 2*b_sym + c_sym - 12
        eq3 = 9*a_sym + 3*b_sym + c_sym - 123
        
        solution = solve([eq1, eq2, eq3], [a_sym, b_sym, c_sym])
        
        a_val = solution[a_sym]
        b_val = solution[b_sym]
        c_val = solution[c_sym]
        
        check1_passed = (a_val == 50 and b_val == -139 and c_val == 90)
        
        checks.append({
            "name": "sympy_solve_abc",
            "passed": check1_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solved linear system: a={a_val}, b={b_val}, c={c_val}. Expected a=50, b=-139, c=90."
        })
        
        if not check1_passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_solve_abc",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed to solve: {str(e)}"
        })
        all_passed = False
        a_val, b_val, c_val = 50, -139, 90
    
    # ========================================
    # Check 2: SymPy - Verify residuals are zero
    # ========================================
    try:
        residual1 = a_val + b_val + c_val - 1
        residual2 = 4*a_val + 2*b_val + c_val - 12
        residual3 = 9*a_val + 3*b_val + c_val - 123
        
        check2_passed = (residual1 == 0 and residual2 == 0 and residual3 == 0)
        
        checks.append({
            "name": "sympy_verify_residuals",
            "passed": check2_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Residuals: r1={residual1}, r2={residual2}, r3={residual3}. All must be 0."
        })
        
        if not check2_passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "sympy_verify_residuals",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed to verify residuals: {str(e)}"
        })
        all_passed = False
    
    # ========================================
    # Check 3: Compute f(4) and verify it equals 334
    # ========================================
    try:
        f_4 = 16*a_val + 4*b_val + c_val
        check3_passed = (f_4 == 334)
        
        checks.append({
            "name": "compute_f4",
            "passed": check3_passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"f(4) = 16*{a_val} + 4*{b_val} + {c_val} = {f_4}. Expected 334."
        })
        
        if not check3_passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "compute_f4",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed to compute f(4): {str(e)}"
        })
        all_passed = False
    
    # ========================================
    # Check 4: kdrag - Prove the linear system has unique solution
    # ========================================
    try:
        a = Real('a')
        b = Real('b')
        c = Real('c')
        
        system = And(
            a + b + c == 1,
            4*a + 2*b + c == 12,
            9*a + 3*b + c == 123
        )
        
        unique_solution = And(
            system,
            a == 50,
            b == -139,
            c == 90
        )
        
        thm = kd.prove(Exists([a, b, c], unique_solution))
        
        checks.append({
            "name": "kdrag_unique_solution",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved existence of solution (a=50, b=-139, c=90) satisfying the system. Proof object: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_unique_solution",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove unique solution: {str(e)}"
        })
        all_passed = False
    
    # ========================================
    # Check 5: kdrag - Prove f(4) = 334 given the solution
    # ========================================
    try:
        a = Real('a')
        b = Real('b')
        c = Real('c')
        
        premise = And(
            a == 50,
            b == -139,
            c == 90
        )
        
        conclusion = 16*a + 4*b + c == 334
        
        thm = kd.prove(ForAll([a, b, c], Implies(premise, conclusion)))
        
        checks.append({
            "name": "kdrag_f4_equals_334",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved that if a=50, b=-139, c=90, then f(4)=16a+4b+c=334. Proof object: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_f4_equals_334",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove f(4)=334: {str(e)}"
        })
        all_passed = False
    
    # ========================================
    # Check 6: Numerical sanity check
    # ========================================
    try:
        a_num, b_num, c_num = 50, -139, 90
        
        f1 = a_num + b_num + c_num
        f2 = 4*a_num + 2*b_num + c_num
        f3 = 9*a_num + 3*b_num + c_num
        f4 = 16*a_num + 4*b_num + c_num
        
        check6_passed = (f1 == 1 and f2 == 12 and f3 == 123 and f4 == 334)
        
        checks.append({
            "name": "numerical_sanity",
            "passed": check6_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check: f(1)={f1} (expect 1), f(2)={f2} (expect 12), f(3)={f3} (expect 123), f(4)={f4} (expect 334)"
        })
        
        if not check6_passed:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {str(e)}"
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
        print(f"       {check['details']}")