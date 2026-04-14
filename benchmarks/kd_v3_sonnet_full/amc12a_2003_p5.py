import kdrag as kd
from kdrag.smt import *
from sympy import symbols as sp_symbols, solve as sp_solve, Integer as sp_Integer

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Z3 proof that the equation system has unique solution A=6, M=1, C=7
    check1 = {"name": "z3_unique_solution", "backend": "kdrag", "proof_type": "certificate"}
    try:
        A, M, C = Ints("A M C")
        AMC10_val = 10000*A + 1000*M + 100*C + 10
        AMC12_val = 10000*A + 1000*M + 100*C + 12
        
        constraints = And(
            A >= 1, A <= 9,
            M >= 0, M <= 9,
            C >= 0, C <= 9,
            AMC10_val + AMC12_val == 123422
        )
        
        solution = And(A == 6, M == 1, C == 7)
        
        # Prove that constraints imply the solution
        thm = kd.prove(Implies(constraints, solution))
        check1["passed"] = True
        check1["details"] = f"Z3 proved that A=6, M=1, C=7 is the unique solution. Proof object: {thm}"
    except Exception as e:
        check1["passed"] = False
        check1["details"] = f"Z3 proof failed: {str(e)}"
        all_passed = False
    checks.append(check1)
    
    # Check 2: Verify A+M+C=14 given the solution
    check2 = {"name": "z3_sum_equals_14", "backend": "kdrag", "proof_type": "certificate"}
    try:
        A, M, C = Ints("A M C")
        hypothesis = And(A == 6, M == 1, C == 7)
        conclusion = A + M + C == 14
        
        thm2 = kd.prove(Implies(hypothesis, conclusion))
        check2["passed"] = True
        check2["details"] = f"Z3 proved A+M+C=14. Proof object: {thm2}"
    except Exception as e:
        check2["passed"] = False
        check2["details"] = f"Z3 proof failed: {str(e)}"
        all_passed = False
    checks.append(check2)
    
    # Check 3: Algebraic derivation using SymPy
    check3 = {"name": "sympy_algebraic_solution", "backend": "sympy", "proof_type": "symbolic_zero"}
    try:
        a_sym, m_sym, c_sym = sp_symbols('a m c', integer=True)
        
        # AMC10 + AMC12 = 123422
        # (10000a + 1000m + 100c + 10) + (10000a + 1000m + 100c + 12) = 123422
        # 20000a + 2000m + 200c + 22 = 123422
        # 20000a + 2000m + 200c = 123400
        # 200(100a + 10m + c) = 123400
        # 100a + 10m + c = 617
        
        eq = 100*a_sym + 10*m_sym + c_sym - 617
        
        # With digit constraints, solve
        solutions = []
        for a_val in range(1, 10):
            for m_val in range(0, 10):
                for c_val in range(0, 10):
                    if 100*a_val + 10*m_val + c_val == 617:
                        solutions.append((a_val, m_val, c_val))
        
        if len(solutions) == 1 and solutions[0] == (6, 1, 7):
            sum_val = sum(solutions[0])
            if sum_val == 14:
                check3["passed"] = True
                check3["details"] = f"SymPy algebraic solution: A=6, M=1, C=7 is unique. Sum=14"
            else:
                check3["passed"] = False
                check3["details"] = f"Sum is {sum_val}, not 14"
                all_passed = False
        else:
            check3["passed"] = False
            check3["details"] = f"Solutions found: {solutions}"
            all_passed = False
    except Exception as e:
        check3["passed"] = False
        check3["details"] = f"SymPy verification failed: {str(e)}"
        all_passed = False
    checks.append(check3)
    
    # Check 4: Numerical verification
    check4 = {"name": "numerical_verification", "backend": "numerical", "proof_type": "numerical"}
    try:
        A_val, M_val, C_val = 6, 1, 7
        AMC10 = 10000*A_val + 1000*M_val + 100*C_val + 10  # 61710
        AMC12 = 10000*A_val + 1000*M_val + 100*C_val + 12  # 61712
        total = AMC10 + AMC12
        
        if total == 123422 and A_val + M_val + C_val == 14:
            check4["passed"] = True
            check4["details"] = f"Numerical: 61710 + 61712 = {total}, A+M+C = {A_val+M_val+C_val}"
        else:
            check4["passed"] = False
            check4["details"] = f"Numerical check failed: sum={total}, A+M+C={A_val+M_val+C_val}"
            all_passed = False
    except Exception as e:
        check4["passed"] = False
        check4["details"] = f"Numerical verification failed: {str(e)}"
        all_passed = False
    checks.append(check4)
    
    # Check 5: Direct Z3 proof of the complete theorem
    check5 = {"name": "z3_complete_theorem", "backend": "kdrag", "proof_type": "certificate"}
    try:
        A, M, C = Ints("A M C")
        
        # Full theorem: if digits satisfy constraints and equation, then sum is 14
        premise = And(
            A >= 1, A <= 9,
            M >= 0, M <= 9,
            C >= 0, C <= 9,
            (10000*A + 1000*M + 100*C + 10) + (10000*A + 1000*M + 100*C + 12) == 123422
        )
        
        conclusion = A + M + C == 14
        
        thm_complete = kd.prove(Implies(premise, conclusion))
        check5["passed"] = True
        check5["details"] = f"Z3 proved complete theorem: constraints -> A+M+C=14. Proof: {thm_complete}"
    except Exception as e:
        check5["passed"] = False
        check5["details"] = f"Complete theorem proof failed: {str(e)}"
        all_passed = False
    checks.append(check5)
    
    return {"proved": all_passed, "checks": checks}

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']})")
        print(f"    {check['details']}")
    print(f"\nFinal result: A+M+C = 14 is {'VERIFIED' if result['proved'] else 'NOT VERIFIED'}")