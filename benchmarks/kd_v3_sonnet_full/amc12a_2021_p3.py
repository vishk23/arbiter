import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, N

def verify():
    checks = []
    all_passed = True
    
    # CHECK 1: Prove unique solution a = 1582
    try:
        a = Int('a')
        constraint = And(a > 0, 11*a == 17402)
        solution_proof = kd.prove(Implies(constraint, a == 1582))
        
        checks.append({
            'name': 'unique_solution',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that if a > 0 and 11a = 17402, then a = 1582. Proof: {solution_proof}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'unique_solution',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove a = 1582: {str(e)}'
        })
    
    # CHECK 2: Prove the sum constraint holds
    try:
        a = Int('a')
        sum_proof = kd.prove(Implies(a == 1582, 10*a + a == 17402))
        
        checks.append({
            'name': 'sum_constraint',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that 10*1582 + 1582 = 17402. Proof: {sum_proof}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'sum_constraint',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove sum constraint: {str(e)}'
        })
    
    # CHECK 3: Prove the difference is 14238
    try:
        a = Int('a')
        diff_proof = kd.prove(Implies(a == 1582, 10*a - a == 14238))
        
        checks.append({
            'name': 'difference_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that 10*1582 - 1582 = 14238. Proof: {diff_proof}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'difference_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove difference: {str(e)}'
        })
    
    # CHECK 4: Prove divisibility by 10
    try:
        a = Int('a')
        div_proof = kd.prove(Implies(a == 1582, (10*a) % 10 == 0))
        
        checks.append({
            'name': 'divisibility_by_10',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that 10*1582 is divisible by 10. Proof: {div_proof}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'divisibility_by_10',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove divisibility: {str(e)}'
        })
    
    # CHECK 5: Prove both numbers are positive
    try:
        a = Int('a')
        pos_proof = kd.prove(Implies(a == 1582, And(a > 0, 10*a > 0)))
        
        checks.append({
            'name': 'positivity',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that both 1582 and 15820 are positive. Proof: {pos_proof}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'positivity',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove positivity: {str(e)}'
        })
    
    # CHECK 6: Numerical sanity check
    try:
        a_val = 1582
        larger = 10 * a_val
        smaller = a_val
        computed_sum = larger + smaller
        computed_diff = larger - smaller
        
        passed = (computed_sum == 17402 and computed_diff == 14238 and larger % 10 == 0)
        
        checks.append({
            'name': 'numerical_verification',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check: 15820 + 1582 = {computed_sum} (expected 17402), 15820 - 1582 = {computed_diff} (expected 14238), 15820 % 10 = {larger % 10}'
        })
        
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerical_verification',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {str(e)}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print("\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}): {check['details'][:100]}")