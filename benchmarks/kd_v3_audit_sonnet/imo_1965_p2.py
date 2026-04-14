import kdrag as kd
from kdrag.smt import *
import z3

def verify():
    checks = []
    all_passed = True

    # Check 1: Verify trivial solution is always a solution
    try:
        a11, a12, a13 = Reals('a11 a12 a13')
        a21, a22, a23 = Reals('a21 a22 a23')
        a31, a32, a33 = Reals('a31 a32 a33')
        x1, x2, x3 = Reals('x1 x2 x3')
        
        conditions = And(
            a11 > 0, a22 > 0, a33 > 0,
            a12 < 0, a13 < 0, a21 < 0, a23 < 0, a31 < 0, a32 < 0,
            a11 + a12 + a13 > 0,
            a21 + a22 + a23 > 0,
            a31 + a32 + a33 > 0
        )
        
        trivial_is_solution = Implies(
            conditions,
            And(
                a11*0 + a12*0 + a13*0 == 0,
                a21*0 + a22*0 + a23*0 == 0,
                a31*0 + a32*0 + a33*0 == 0
            )
        )
        
        thm1 = kd.prove(ForAll([a11, a12, a13, a21, a22, a23, a31, a32, a33], trivial_is_solution))
        checks.append({
            'name': 'trivial_solution',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Verified that x1=x2=x3=0 is always a solution'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'trivial_solution',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })

    # Check 2: Prove no solution with all positive xi
    try:
        a11, a12, a13 = Reals('a11 a12 a13')
        a21, a22, a23 = Reals('a21 a22 a23')
        a31, a32, a33 = Reals('a31 a32 a33')
        x1, x2, x3 = Reals('x1 x2 x3')
        
        conditions = And(
            a11 > 0, a22 > 0, a33 > 0,
            a12 < 0, a13 < 0, a21 < 0, a23 < 0, a31 < 0, a32 < 0,
            a11 + a12 + a13 > 0,
            a21 + a22 + a23 > 0,
            a31 + a32 + a33 > 0
        )
        
        system = And(
            a11*x1 + a12*x2 + a13*x3 == 0,
            a21*x1 + a22*x2 + a23*x3 == 0,
            a31*x1 + a32*x2 + a33*x3 == 0
        )
        
        all_positive_no_solution = Implies(
            And(conditions, system, x1 > 0, x2 > 0, x3 > 0, x1 <= x2, x2 <= x3),
            False
        )
        
        thm2 = kd.prove(ForAll([a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3], 
                               all_positive_no_solution))
        checks.append({
            'name': 'no_all_positive',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Verified no solution exists with all xi > 0 (ordered)'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'no_all_positive',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })

    # Check 3: Prove no solution with all negative xi
    try:
        a11, a12, a13 = Reals('a11 a12 a13')
        a21, a22, a23 = Reals('a21 a22 a23')
        a31, a32, a33 = Reals('a31 a32 a33')
        x1, x2, x3 = Reals('x1 x2 x3')
        
        conditions = And(
            a11 > 0, a22 > 0, a33 > 0,
            a12 < 0, a13 < 0, a21 < 0, a23 < 0, a31 < 0, a32 < 0,
            a11 + a12 + a13 > 0,
            a21 + a22 + a23 > 0,
            a31 + a32 + a33 > 0
        )
        
        system = And(
            a11*x1 + a12*x2 + a13*x3 == 0,
            a21*x1 + a22*x2 + a23*x3 == 0,
            a31*x1 + a32*x2 + a33*x3 == 0
        )
        
        all_negative_no_solution = Implies(
            And(conditions, system, x1 < 0, x2 < 0, x3 < 0, x1 >= x2, x2 >= x3),
            False
        )
        
        thm3 = kd.prove(ForAll([a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3], 
                               all_negative_no_solution))
        checks.append({
            'name': 'no_all_negative',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Verified no solution exists with all xi < 0 (ordered)'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'no_all_negative',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })

    # Check 4: Prove no solution with mixed signs (2 pos, 1 neg)
    try:
        a11, a12, a13 = Reals('a11 a12 a13')
        a21, a22, a23 = Reals('a21 a22 a23')
        a31, a32, a33 = Reals('a31 a32 a33')
        x1, x2, x3 = Reals('x1 x2 x3')
        
        conditions = And(
            a11 > 0, a22 > 0, a33 > 0,
            a12 < 0, a13 < 0, a21 < 0, a23 < 0, a31 < 0, a32 < 0,
            a11 + a12 + a13 > 0,
            a21 + a22 + a23 > 0,
            a31 + a32 + a33 > 0
        )
        
        system = And(
            a11*x1 + a12*x2 + a13*x3 == 0,
            a21*x1 + a22*x2 + a23*x3 == 0,
            a31*x1 + a32*x2 + a33*x3 == 0
        )
        
        two_pos_one_neg_no_solution = Implies(
            And(conditions, system, x1 > 0, x2 > 0, x3 < 0),
            False
        )
        
        thm4 = kd.prove(ForAll([a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3], 
                               two_pos_one_neg_no_solution))
        checks.append({
            'name': 'no_mixed_2pos_1neg',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Verified no solution exists with x1>0, x2>0, x3<0'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'no_mixed_2pos_1neg',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })

    # Check 5: Prove no solution with mixed signs (1 pos, 2 neg)
    try:
        a11, a12, a13 = Reals('a11 a12 a13')
        a21, a22, a23 = Reals('a21 a22 a23')
        a31, a32, a33 = Reals('a31 a32 a33')
        x1, x2, x3 = Reals('x1 x2 x3')
        
        conditions = And(
            a11 > 0, a22 > 0, a33 > 0,
            a12 < 0, a13 < 0, a21 < 0, a23 < 0, a31 < 0, a32 < 0,
            a11 + a12 + a13 > 0,
            a21 + a22 + a23 > 0,
            a31 + a32 + a33 > 0
        )
        
        system = And(
            a11*x1 + a12*x2 + a13*x3 == 0,
            a21*x1 + a22*x2 + a23*x3 == 0,
            a31*x1 + a32*x2 + a33*x3 == 0
        )
        
        one_pos_two_neg_no_solution = Implies(
            And(conditions, system, x1 > 0, x2 < 0, x3 < 0),
            False
        )
        
        thm5 = kd.prove(ForAll([a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3], 
                               one_pos_two_neg_no_solution))
        checks.append({
            'name': 'no_mixed_1pos_2neg',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Verified no solution exists with x1>0, x2<0, x3<0'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'no_mixed_1pos_2neg',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })

    # Check 6: Numerical verification on concrete example
    try:
        import numpy as np
        A = np.array([[2, -1, -0.5], [-0.5, 3, -1], [-1, -0.5, 4]])
        
        # Check conditions
        assert A[0,0] > 0 and A[1,1] > 0 and A[2,2] > 0
        assert all(A[i,j] < 0 for i in range(3) for j in range(3) if i != j)
        assert all(sum(A[i,:]) > 0 for i in range(3))
        
        # Solve Ax = 0
        _, s, _ = np.linalg.svd(A)
        min_singular = np.min(s)
        
        # Matrix is non-singular (no non-trivial null space)
        is_nonsingular = min_singular > 1e-10
        
        checks.append({
            'name': 'numerical_concrete',
            'passed': is_nonsingular,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Concrete matrix has min singular value {min_singular:.6f}, confirming only trivial solution'
        })
        if not is_nonsingular:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerical_concrete',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Failed: {str(e)}'
        })

    # Check 7: Main theorem - only trivial solution exists
    try:
        a11, a12, a13 = Reals('a11 a12 a13')
        a21, a22, a23 = Reals('a21 a22 a23')
        a31, a32, a33 = Reals('a31 a32 a33')
        x1, x2, x3 = Reals('x1 x2 x3')
        
        conditions = And(
            a11 > 0, a22 > 0, a33 > 0,
            a12 < 0, a13 < 0, a21 < 0, a23 < 0, a31 < 0, a32 < 0,
            a11 + a12 + a13 > 0,
            a21 + a22 + a23 > 0,
            a31 + a32 + a33 > 0
        )
        
        system = And(
            a11*x1 + a12*x2 + a13*x3 == 0,
            a21*x1 + a22*x2 + a23*x3 == 0,
            a31*x1 + a32*x2 + a33*x3 == 0
        )
        
        only_trivial = Implies(
            And(conditions, system),
            And(x1 == 0, x2 == 0, x3 == 0)
        )
        
        thm_main = kd.prove(ForAll([a11, a12, a13, a21, a22, a23, a31, a32, a33, x1, x2, x3], 
                                   only_trivial))
        checks.append({
            'name': 'main_theorem',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Main theorem: system has only trivial solution under given conditions'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'main_theorem',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })

    return {'proved': all_passed, 'checks': checks}

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])})")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']}: {check['details']}")