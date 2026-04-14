import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify, N

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Numerical verification with concrete values
    try:
        # Given: a_1 + a_2 + ... + a_98 = 137
        # With common difference 1: a_n = a_1 + (n-1)
        # Sum formula: n/2 * (2*a_1 + (n-1)*d) = 98/2 * (2*a_1 + 97*1) = 49*(2*a_1 + 97)
        # So: 49*(2*a_1 + 97) = 137
        # Therefore: 2*a_1 + 97 = 137/49
        a_1_numerical = (137/49 - 97) / 2
        
        # Calculate even-indexed sum
        # a_2, a_4, ..., a_98 are 49 terms
        # a_2 = a_1 + 1, a_4 = a_1 + 3, ..., a_98 = a_1 + 97
        # These form AP with first term (a_1 + 1), common diff 2, 49 terms
        even_sum_numerical = 49/2 * (2*(a_1_numerical + 1) + 48*2)
        
        passed = abs(even_sum_numerical - 93) < 1e-10
        checks.append({
            "name": "numerical_verification",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed a_1={a_1_numerical:.10f}, even sum={even_sum_numerical:.10f}, target=93"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "numerical_verification",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 2: Z3 verification using kdrag - prove the algebraic relationship
    try:
        a1 = Real('a1')
        even_sum = Real('even_sum')
        
        # Constraint 1: Total sum = 137
        # Sum of AP: 49*(2*a1 + 97) = 137
        total_sum_constraint = (49 * (2*a1 + 97) == 137)
        
        # Constraint 2: Even-indexed sum formula
        # a_2 + a_4 + ... + a_98 = 49 terms starting at a1+1 with diff 2
        # Sum = 49/2 * (2*(a1+1) + 48*2) = 49/2 * (2*a1 + 2 + 96) = 49/2 * (2*a1 + 98)
        even_sum_formula = (even_sum == 49 * (a1 + 49))
        
        # Prove that under these constraints, even_sum = 93
        theorem = ForAll([a1, even_sum],
            Implies(
                And(total_sum_constraint, even_sum_formula),
                even_sum == 93
            )
        )
        
        proof = kd.prove(theorem)
        
        checks.append({
            "name": "kdrag_algebraic_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified: Given total sum = 137 and AP with d=1, even-indexed sum = 93. Proof object: {proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_algebraic_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_algebraic_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 3: Verify the hint's approach using Z3
    try:
        a2, a4, a98 = Reals('a2 a4 a98')
        even_sum_var = Real('even_sum_var')
        
        # Using the hint: a_{2n-1} = a_{2n} - 1
        # So: (a_2-1) + a_2 + (a_4-1) + a_4 + ... + (a_98-1) + a_98 = 137
        # This simplifies to: 2*(a_2 + a_4 + ... + a_98) - 49 = 137
        # Therefore: a_2 + a_4 + ... + a_98 = (137 + 49)/2 = 93
        
        hint_theorem = ForAll([even_sum_var],
            Implies(
                2 * even_sum_var - 49 == 137,
                even_sum_var == 93
            )
        )
        
        hint_proof = kd.prove(hint_theorem)
        
        checks.append({
            "name": "kdrag_hint_approach",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Z3 verified hint approach: 2*S - 49 = 137 implies S = 93. Proof: {hint_proof}"
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            "name": "kdrag_hint_approach",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {str(e)}"
        })
        all_passed = False
    except Exception as e:
        checks.append({
            "name": "kdrag_hint_approach",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    # Check 4: SymPy symbolic verification
    try:
        a1_sym = symbols('a1', real=True)
        
        # Total sum equation: 49*(2*a1 + 97) = 137
        total_eq = 49*(2*a1_sym + 97) - 137
        a1_solution = simplify(total_eq / 98)  # Solve for a1
        
        # a1 = (137/49 - 97)/2 = (137 - 97*49)/(49*2) = (137 - 4753)/98 = -4616/98 = -2308/49
        a1_exact = (137 - 97*49) / 98
        
        # Even sum = 49*(a1 + 49)
        even_sum_symbolic = 49 * (a1_exact + 49)
        
        # Verify it equals 93
        result = simplify(even_sum_symbolic - 93)
        
        passed = (result == 0)
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic computation: a1={a1_exact}, even_sum={even_sum_symbolic}, difference from 93: {result}"
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            "name": "sympy_symbolic_verification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Error: {str(e)}"
        })
        all_passed = False
    
    return {
        "proved": all_passed,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} ({check['backend']})")
        print(f"    {check['details']}")
    print(f"\nConclusion: The answer is 093, and this has been {'VERIFIED' if result['proved'] else 'NOT VERIFIED'}.")