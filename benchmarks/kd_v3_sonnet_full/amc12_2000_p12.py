import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, simplify

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the algebraic identity (A+1)(M+1)(C+1) = AMC + AM + AC + MC + A + M + C + 1
    try:
        from sympy import symbols, expand
        A_sym, M_sym, C_sym = symbols('A M C')
        lhs = (A_sym + 1) * (M_sym + 1) * (C_sym + 1)
        rhs = A_sym*M_sym*C_sym + A_sym*M_sym + A_sym*C_sym + M_sym*C_sym + A_sym + M_sym + C_sym + 1
        diff = expand(lhs - rhs)
        
        checks.append({
            "name": "algebraic_identity",
            "passed": diff == 0,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified (A+1)(M+1)(C+1) = AMC + AM + AC + MC + A + M + C + 1. Difference: {diff}"
        })
        if diff != 0:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "algebraic_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed to verify identity: {e}"
        })
        all_passed = False
    
    # Check 2: Verify that when A+M+C=12, the expression becomes (A+1)(M+1)(C+1) - 13
    try:
        A_sym, M_sym, C_sym = symbols('A M C')
        # Given A + M + C = 12
        expr = A_sym*M_sym*C_sym + A_sym*M_sym + A_sym*C_sym + M_sym*C_sym
        identity_form = (A_sym + 1)*(M_sym + 1)*(C_sym + 1) - (A_sym + M_sym + C_sym) - 1
        # Substitute A + M + C = 12
        identity_with_constraint = (A_sym + 1)*(M_sym + 1)*(C_sym + 1) - 13
        
        diff = expand(expr - identity_form)
        
        checks.append({
            "name": "constraint_substitution",
            "passed": diff == 0,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified AMC + AM + AC + MC = (A+1)(M+1)(C+1) - (A+M+C) - 1. When A+M+C=12, this is (A+1)(M+1)(C+1) - 13"
        })
        if diff != 0:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "constraint_substitution",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 3: Verify A=M=C=4 gives 112 using kdrag
    try:
        A, M, C = Ints('A M C')
        result = Int('result')
        
        # Define the constraint and the value at A=M=C=4
        constraint = And(A == 4, M == 4, C == 4)
        value_expr = A*M*C + A*M + M*C + A*C
        
        # Prove that when A=M=C=4, the expression equals 112
        thm = kd.prove(Implies(constraint, value_expr == 112))
        
        checks.append({
            "name": "optimal_value_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: A=M=C=4 implies AMC+AM+MC+AC=112. Proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "optimal_value_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove optimal value: {e}"
        })
        all_passed = False
    
    # Check 4: Verify A+M+C=12 when A=M=C=4
    try:
        A, M, C = Ints('A M C')
        constraint = And(A == 4, M == 4, C == 4)
        sum_eq_12 = (A + M + C == 12)
        
        thm = kd.prove(Implies(constraint, sum_eq_12))
        
        checks.append({
            "name": "constraint_satisfaction",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: A=M=C=4 satisfies A+M+C=12. Proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "constraint_satisfaction",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed: {e}"
        })
        all_passed = False
    
    # Check 5: Verify no nonnegative integer solution gives value > 112
    try:
        A, M, C = Ints('A M C')
        value_expr = A*M*C + A*M + M*C + A*C
        
        # Prove that for all nonnegative integers with sum 12, value <= 112
        constraint = And(A >= 0, M >= 0, C >= 0, A + M + C == 12)
        claim = ForAll([A, M, C], Implies(constraint, value_expr <= 112))
        
        thm = kd.prove(claim)
        
        checks.append({
            "name": "optimality_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: For all A,M,C >= 0 with A+M+C=12, AMC+AM+MC+AC <= 112. Proof: {thm}"
        })
    except Exception as e:
        checks.append({
            "name": "optimality_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove optimality (Z3 may timeout on nonlinear): {e}"
        })
        all_passed = False
    
    # Check 6: Numerical verification - test several cases
    try:
        test_cases = [
            (4, 4, 4, 112),
            (0, 6, 6, 72),
            (3, 4, 5, 71),
            (2, 5, 5, 72),
            (6, 3, 3, 63),
            (0, 0, 12, 0),
            (1, 1, 10, 21)
        ]
        
        all_correct = True
        details_list = []
        for a, m, c in [(a, m, c) for a, m, c, _ in test_cases]:
            if a + m + c == 12 and a >= 0 and m >= 0 and c >= 0:
                value = a*m*c + a*m + m*c + a*c
                expected = [v for ta, tm, tc, v in test_cases if ta == a and tm == m and tc == c][0]
                if value == expected:
                    details_list.append(f"({a},{m},{c}) -> {value}")
                    if value > 112:
                        all_correct = False
                else:
                    all_correct = False
        
        checks.append({
            "name": "numerical_verification",
            "passed": all_correct,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Tested cases: {'; '.join(details_list)}. Max is 112 at (4,4,4)"
        })
        if not all_correct:
            all_passed = False
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Failed: {e}"
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
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']})")
        print(f"  {check['details']}")