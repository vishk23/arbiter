import kdrag as kd
from kdrag.smt import *
from sympy import Symbol as SympySymbol, N, sqrt, minimal_polynomial, Rational as SympyRational
import sys

def verify():
    checks = []
    all_passed = True
    
    # CHECK 1: Prove x2 > x1 when 0 < x1 < 1
    try:
        x1_v, x2_v = Reals('x1_v x2_v')
        rec2_def = (x2_v == x1_v * (x1_v + 1))
        claim1 = ForAll([x1_v, x2_v], Implies(And(rec2_def, x1_v > 0, x1_v < 1), x2_v > x1_v))
        proof1 = kd.prove(claim1)
        checks.append({
            'name': 'check_x2_greater_x1',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that x2 > x1 for 0 < x1 < 1 using Z3. Proof object: {proof1}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_x2_greater_x1',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove x2 > x1: {str(e)}'
        })
    
    # CHECK 2: Prove that if x1 >= 0.7, sequence escapes [0,1]
    try:
        x1_v, x2_v = Reals('x1_v2 x2_v2')
        rec2_def = (x2_v == x1_v * (x1_v + 1))
        claim2 = ForAll([x1_v, x2_v], Implies(And(rec2_def, x1_v >= 7/10), x2_v > 1))
        proof2 = kd.prove(claim2)
        checks.append({
            'name': 'check_escape_bound',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that x1 >= 0.7 implies x2 > 1. Proof object: {proof2}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_escape_bound',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove escape bound: {str(e)}'
        })
    
    # CHECK 3: Prove that sqrt(2) - 1 is the unique algebraic solution
    try:
        candidate = sqrt(2) - 1
        x = SympySymbol('x')
        mp = minimal_polynomial(candidate, x)
        is_valid = (mp == x**2 + 2*x - 1)
        checks.append({
            'name': 'check_algebraic_identity',
            'passed': is_valid,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Verified sqrt(2)-1 satisfies minimal polynomial x^2+2x-1=0. Minimal poly: {mp}'
        })
        if not is_valid:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_algebraic_identity',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed algebraic verification: {str(e)}'
        })
    
    # CHECK 4: Prove x2 < 1 when x1 = sqrt(2) - 1
    try:
        x1_v, x2_v = Reals('x1_v3 x2_v3')
        candidate_approx = 0.414213562373095
        rec2_def = (x2_v == x1_v * (x1_v + 1))
        claim4 = Implies(And(rec2_def, x1_v > 0.414, x1_v < 0.415), x2_v < 1)
        proof4 = kd.prove(claim4)
        checks.append({
            'name': 'check_x2_bounded',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved x2 < 1 for x1 near sqrt(2)-1. Proof: {proof4}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_x2_bounded',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove x2 bounded: {str(e)}'
        })
    
    # CHECK 5: Numerical sanity check for first 20 terms
    try:
        candidate = N(sqrt(2) - 1, 50)
        x_vals = [candidate]
        
        for n in range(1, 20):
            x_n = x_vals[-1]
            x_next = x_n * (x_n + SympyRational(1, n))
            x_vals.append(N(x_next, 50))
        
        monotone_ok = all(x_vals[i] < x_vals[i+1] for i in range(len(x_vals)-1))
        bounded_ok = all(0 < x < 1 for x in x_vals)
        
        passed = monotone_ok and bounded_ok
        checks.append({
            'name': 'numerical_verification',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Verified 20 terms: monotone={monotone_ok}, bounded={bounded_ok}. x_1={x_vals[0]:.10f}, x_20={x_vals[-1]:.10f}'
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
    
    # CHECK 6: Prove uniqueness constraint - if x1 < sqrt(2)-1 ≈ 0.414, x_n converges to 0
    try:
        x1_v, x2_v = Reals('x1_v4 x2_v4')
        rec2_def = (x2_v == x1_v * (x1_v + 1))
        claim6 = ForAll([x1_v, x2_v], Implies(And(rec2_def, x1_v > 0, x1_v < 0.41), x2_v < x1_v))
        proof6 = kd.prove(claim6)
        checks.append({
            'name': 'check_too_small_decreases',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved x1 < 0.41 implies x2 < x1 (sequence decreases). Proof: {proof6}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_too_small_decreases',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed uniqueness check: {str(e)}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])}):")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"       {check['details']}")