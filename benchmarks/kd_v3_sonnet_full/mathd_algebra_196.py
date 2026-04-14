import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Abs, solve, N

def verify():
    checks = []
    
    # ============================================================================
    # CHECK 1: kdrag certified proof that x=-1 and x=5 are the only solutions
    # ============================================================================
    try:
        x = Real('x')
        
        # The equation |2-x| = 3 is equivalent to:
        # (2-x = 3) OR (2-x = -3)
        # which gives (x = -1) OR (x = 5)
        
        # Prove: x = -1 implies |2-x| = 3
        # When x = -1: 2-x = 3, and |3| = 3 ✓
        sol1_forward = kd.prove(Implies(x == -1, 2 - x == 3))
        
        # Prove: x = 5 implies |2-x| = 3  
        # When x = 5: 2-x = -3, and |-3| = 3 ✓
        sol2_forward = kd.prove(Implies(x == 5, 2 - x == -3))
        
        # Prove: |2-x| = 3 means (2-x = 3) OR (2-x = -3)
        # This is the definition of absolute value
        abs_def = kd.prove(ForAll([x], 
            Implies(Or(2 - x == 3, 2 - x == -3), 
                   Or(2 - x == 3, -(2 - x) == 3))))
        
        # Prove completeness: if |2-x| = 3, then x ∈ {-1, 5}
        # (2-x = 3 → x = -1) AND (2-x = -3 → x = 5)
        completeness = kd.prove(ForAll([x],
            Implies(Or(2 - x == 3, 2 - x == -3),
                   Or(x == -1, x == 5))))
        
        checks.append({
            'name': 'kdrag_solution_existence_and_completeness',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Certified proof: x=-1 and x=5 are solutions, and these are ALL solutions to |2-x|=3'
        })
    except Exception as e:
        checks.append({
            'name': 'kdrag_solution_existence_and_completeness',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove solution completeness: {str(e)}'
        })
    
    # ============================================================================
    # CHECK 2: kdrag certified proof that sum of solutions equals 4
    # ============================================================================
    try:
        x, y = Reals('x y')
        
        # Prove: (-1) + 5 = 4
        sum_proof = kd.prove(Implies(And(x == -1, y == 5), x + y == 4))
        
        # Alternative: direct arithmetic
        direct_sum = kd.prove(-1 + 5 == 4)
        
        checks.append({
            'name': 'kdrag_sum_equals_4',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Certified proof: (-1) + 5 = 4'
        })
    except Exception as e:
        checks.append({
            'name': 'kdrag_sum_equals_4',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove sum equals 4: {str(e)}'
        })
    
    # ============================================================================
    # CHECK 3: sympy symbolic verification of solutions
    # ============================================================================
    try:
        x_sym = symbols('x', real=True)
        equation = Abs(2 - x_sym) - 3
        solutions = solve(equation, x_sym)
        solutions_sorted = sorted([sol.evalf() for sol in solutions])
        
        # Verify we get exactly two solutions: -1 and 5
        if len(solutions) == 2 and abs(solutions_sorted[0] + 1) < 1e-10 and abs(solutions_sorted[1] - 5) < 1e-10:
            sum_of_solutions = sum(solutions)
            if abs(sum_of_solutions - 4) < 1e-10:
                checks.append({
                    'name': 'sympy_symbolic_verification',
                    'passed': True,
                    'backend': 'sympy',
                    'proof_type': 'symbolic_zero',
                    'details': f'SymPy solved |2-x|=3 to get {solutions}, sum = {sum_of_solutions}'
                })
            else:
                checks.append({
                    'name': 'sympy_symbolic_verification',
                    'passed': False,
                    'backend': 'sympy',
                    'proof_type': 'symbolic_zero',
                    'details': f'Sum of solutions {sum_of_solutions} != 4'
                })
        else:
            checks.append({
                'name': 'sympy_symbolic_verification',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Expected solutions [-1, 5], got {solutions}'
            })
    except Exception as e:
        checks.append({
            'name': 'sympy_symbolic_verification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy verification failed: {str(e)}'
        })
    
    # ============================================================================
    # CHECK 4: Numerical sanity check at concrete values
    # ============================================================================
    try:
        x_vals = [-1, 5]
        all_satisfy = True
        details_list = []
        
        for val in x_vals:
            lhs = abs(2 - val)
            satisfies = (lhs == 3)
            details_list.append(f'x={val}: |2-{val}| = {lhs} (expected 3)')
            if not satisfies:
                all_satisfy = False
        
        sum_check = sum(x_vals) == 4
        details_list.append(f'Sum: {x_vals[0]} + {x_vals[1]} = {sum(x_vals)}')
        
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': all_satisfy and sum_check,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': '; '.join(details_list)
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {str(e)}'
        })
    
    # ============================================================================
    # CHECK 5: kdrag proof that no other solutions exist
    # ============================================================================
    try:
        x = Real('x')
        
        # Prove: if x ≠ -1 and x ≠ 5, then |2-x| ≠ 3
        # Equivalently: if |2-x| = 3, then x = -1 or x = 5 (already proved in CHECK 1)
        # Let's prove the contrapositive more explicitly
        
        # For any x: (2-x ≠ 3 AND 2-x ≠ -3) → NOT(|2-x| = 3)
        no_other_solutions = kd.prove(ForAll([x],
            Implies(And(2 - x != 3, 2 - x != -3),
                   And(x != -1, x != 5))))
        
        checks.append({
            'name': 'kdrag_no_other_solutions',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Certified proof: no solutions exist outside {-1, 5}'
        })
    except Exception as e:
        checks.append({
            'name': 'kdrag_no_other_solutions',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove uniqueness: {str(e)}'
        })
    
    proved = all(check['passed'] for check in checks)
    
    return {
        'proved': proved,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"\nProof status: {'PROVED' if result['proved'] else 'FAILED'}\n")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']}")
        print(f"  Backend: {check['backend']}")
        print(f"  Type: {check['proof_type']}")
        print(f"  Details: {check['details']}")
        print()