import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, simplify

def verify():
    checks = []
    all_passed = True
    
    # ═══════════════════════════════════════════════════════════
    # CHECK 1: kdrag proof of arithmetic sequence properties
    # ═══════════════════════════════════════════════════════════
    try:
        a, d = Reals('a d')
        
        # Define the constraints from the problem
        constraint_7 = (a + 6*d == 30)
        constraint_11 = (a + 10*d == 60)
        
        # Prove that d = 15/2 follows from the constraints
        d_value_thm = kd.prove(
            Implies(
                And(a + 6*d == 30, a + 10*d == 60),
                d == RealVal(15)/RealVal(2)
            )
        )
        
        # Prove that a = -15 follows from the constraints
        a_value_thm = kd.prove(
            Implies(
                And(a + 6*d == 30, a + 10*d == 60),
                a == -15
            )
        )
        
        # Prove the 21st term is 135
        term_21_thm = kd.prove(
            Implies(
                And(a + 6*d == 30, a + 10*d == 60),
                a + 20*d == 135
            )
        )
        
        checks.append({
            'name': 'kdrag_arithmetic_sequence_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Successfully proved: (1) d = 15/2, (2) a = -15, (3) 21st term = 135. Proof objects: {d_value_thm}, {a_value_thm}, {term_21_thm}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'kdrag_arithmetic_sequence_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {str(e)}'
        })
    
    # ═══════════════════════════════════════════════════════════
    # CHECK 2: SymPy symbolic verification
    # ═══════════════════════════════════════════════════════════
    try:
        a_sym, d_sym = symbols('a d', real=True)
        
        # Solve for a and d
        eq1 = Eq(a_sym + 6*d_sym, 30)
        eq2 = Eq(a_sym + 10*d_sym, 60)
        solution = solve([eq1, eq2], [a_sym, d_sym])
        
        a_val = solution[a_sym]
        d_val = solution[d_sym]
        
        # Compute 21st term
        term_21 = a_val + 20*d_val
        
        # Verify the result
        is_correct = simplify(term_21 - 135) == 0
        
        checks.append({
            'name': 'sympy_symbolic_verification',
            'passed': is_correct,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Solved system: a = {a_val}, d = {d_val}. 21st term = {term_21}. Verification: {term_21} - 135 = {simplify(term_21 - 135)}'
        })
        
        if not is_correct:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'sympy_symbolic_verification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy verification failed: {str(e)}'
        })
    
    # ═══════════════════════════════════════════════════════════
    # CHECK 3: Numerical sanity check
    # ═══════════════════════════════════════════════════════════
    try:
        # Using exact values from the proof
        a_num = -15.0
        d_num = 7.5  # 15/2
        
        # Check 7th term
        term_7 = a_num + 6*d_num
        check_7 = abs(term_7 - 30.0) < 1e-10
        
        # Check 11th term
        term_11 = a_num + 10*d_num
        check_11 = abs(term_11 - 60.0) < 1e-10
        
        # Check 21st term
        term_21_num = a_num + 20*d_num
        check_21 = abs(term_21_num - 135.0) < 1e-10
        
        passed = check_7 and check_11 and check_21
        
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'With a={a_num}, d={d_num}: 7th term={term_7} (expected 30), 11th term={term_11} (expected 60), 21st term={term_21_num} (expected 135)'
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {str(e)}'
        })
    
    # ═══════════════════════════════════════════════════════════
    # CHECK 4: Alternative kdrag proof using direct substitution
    # ═══════════════════════════════════════════════════════════
    try:
        a, d = Reals('a d')
        
        # Prove the difference equation: (a + 10d) - (a + 6d) = 30
        diff_thm = kd.prove(
            Implies(
                And(a + 6*d == 30, a + 10*d == 60),
                4*d == 30
            )
        )
        
        # Prove 21st term formula using 11th term + 10d
        formula_thm = kd.prove(
            Implies(
                And(a + 10*d == 60, d == RealVal(15)/RealVal(2)),
                a + 20*d == 135
            )
        )
        
        checks.append({
            'name': 'kdrag_alternative_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Alternative proof: (1) Proved 4d = 30 from constraints, (2) Proved 21st term = 135 using 11th term formula. Proofs: {diff_thm}, {formula_thm}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'kdrag_alternative_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Alternative kdrag proof failed: {str(e)}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])}):")
    for i, check in enumerate(result['checks'], 1):
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} [{check['backend']}] {check['name']}")
        print(f"    {check['details']}")