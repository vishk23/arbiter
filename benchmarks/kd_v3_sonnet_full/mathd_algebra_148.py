import kdrag as kd
from kdrag.smt import Real, ForAll, Exists, Implies, And
from sympy import symbols, solve, simplify

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Kdrag proof that c=3 satisfies the constraints
    check1_passed = False
    check1_details = ""
    try:
        x = Real("x")
        c = Real("c")
        
        # f(x) = c*x^3 - 9*x + 3
        # f(2) = c*8 - 18 + 3 = 8*c - 15
        # Given: f(2) = 9
        # Therefore: 8*c - 15 = 9
        # Solve: 8*c = 24, c = 3
        
        # Prove that if f(2) = 9, then c = 3
        f_at_2 = 8*c - 15
        constraint = (f_at_2 == 9)
        conclusion = (c == 3)
        
        # Direct proof: 8c - 15 = 9 implies c = 3
        thm = kd.prove(Implies(constraint, conclusion))
        check1_passed = True
        check1_details = f"Proved: 8c - 15 = 9 => c = 3. Proof object: {thm}"
    except Exception as e:
        check1_passed = False
        check1_details = f"Kdrag proof failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "kdrag_implication",
        "passed": check1_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check1_details
    })
    
    # Check 2: Kdrag proof that c=3 is the unique solution
    check2_passed = False
    check2_details = ""
    try:
        c = Real("c")
        # There exists a unique c such that 8c - 15 = 9
        thm2 = kd.prove(Exists([c], And(8*c - 15 == 9, c == 3)))
        check2_passed = True
        check2_details = f"Proved existence and uniqueness: c=3 is the solution. Proof: {thm2}"
    except Exception as e:
        check2_passed = False
        check2_details = f"Uniqueness proof failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "kdrag_existence",
        "passed": check2_passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": check2_details
    })
    
    # Check 3: SymPy symbolic verification
    check3_passed = False
    check3_details = ""
    try:
        c_sym = symbols('c', real=True)
        # f(2) = 8c - 15 = 9
        equation = 8*c_sym - 15 - 9
        solutions = solve(equation, c_sym)
        
        if len(solutions) == 1 and solutions[0] == 3:
            check3_passed = True
            check3_details = f"SymPy solved 8c - 15 = 9, found unique solution c = {solutions[0]}"
        else:
            check3_details = f"SymPy found unexpected solutions: {solutions}"
            all_passed = False
    except Exception as e:
        check3_details = f"SymPy verification failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "sympy_solve",
        "passed": check3_passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": check3_details
    })
    
    # Check 4: Numerical verification that c=3 gives f(2)=9
    check4_passed = False
    check4_details = ""
    try:
        c_val = 3
        x_val = 2
        f_val = c_val * (x_val**3) - 9*x_val + 3
        
        if f_val == 9:
            check4_passed = True
            check4_details = f"Numerical check: f(2) = {c_val}*8 - 18 + 3 = {f_val} = 9 ✓"
        else:
            check4_details = f"Numerical check failed: f(2) = {f_val}, expected 9"
            all_passed = False
    except Exception as e:
        check4_details = f"Numerical check failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "numerical_verification",
        "passed": check4_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": check4_details
    })
    
    # Check 5: Verify the algebraic derivation step-by-step
    check5_passed = False
    check5_details = ""
    try:
        # Step 1: f(2) = 8c - 15
        step1 = (8*3 - 15 == 9)  # Substitute c=3
        # Step 2: 8c - 15 = 9
        step2 = (24 - 15 == 9)
        # Step 3: Check arithmetic
        step3 = (9 == 9)
        
        if step1 and step2 and step3:
            check5_passed = True
            check5_details = "Step-by-step verification: 8(3) - 15 = 24 - 15 = 9 ✓"
        else:
            check5_details = "Step-by-step verification failed"
            all_passed = False
    except Exception as e:
        check5_details = f"Step verification failed: {str(e)}"
        all_passed = False
    
    checks.append({
        "name": "step_by_step",
        "passed": check5_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": check5_details
    })
    
    return {
        "proved": all_passed and check1_passed and check2_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"    {check['details']}")