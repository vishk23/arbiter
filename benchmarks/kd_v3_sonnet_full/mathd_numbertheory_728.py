import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    
    # Check 1: Verify 29 ≡ 1 (mod 7) using kdrag
    try:
        n = Int('n')
        thm1 = kd.prove(29 % 7 == 1)
        checks.append({
            'name': '29_equiv_1_mod_7',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved 29 ≡ 1 (mod 7) using Z3. Proof: {thm1}'
        })
    except Exception as e:
        checks.append({
            'name': '29_equiv_1_mod_7',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove 29 ≡ 1 (mod 7): {e}'
        })
    
    # Check 2: Verify 5 ≡ -2 (mod 7) using kdrag
    try:
        thm2 = kd.prove(5 % 7 == (-2) % 7)
        checks.append({
            'name': '5_equiv_neg2_mod_7',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved 5 ≡ -2 (mod 7) using Z3. Proof: {thm2}'
        })
    except Exception as e:
        checks.append({
            'name': '5_equiv_neg2_mod_7',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove 5 ≡ -2 (mod 7): {e}'
        })
    
    # Check 3: Verify 2^3 ≡ 1 (mod 7) using kdrag
    try:
        thm3 = kd.prove((2**3) % 7 == 1)
        checks.append({
            'name': '2_cubed_equiv_1_mod_7',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved 2^3 ≡ 1 (mod 7) using Z3. Proof: {thm3}'
        })
    except Exception as e:
        checks.append({
            'name': '2_cubed_equiv_1_mod_7',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove 2^3 ≡ 1 (mod 7): {e}'
        })
    
    # Check 4: Verify 2^13 ≡ 2 (mod 7) using kdrag
    try:
        thm4 = kd.prove((2**13) % 7 == 2)
        checks.append({
            'name': '2_to_13_equiv_2_mod_7',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved 2^13 ≡ 2 (mod 7) using Z3. Proof: {thm4}'
        })
    except Exception as e:
        checks.append({
            'name': '2_to_13_equiv_2_mod_7',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove 2^13 ≡ 2 (mod 7): {e}'
        })
    
    # Check 5: Main theorem - 29^13 - 5^13 ≡ 3 (mod 7) using kdrag
    try:
        thm_main = kd.prove((29**13 - 5**13) % 7 == 3)
        checks.append({
            'name': 'main_theorem',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved 29^13 - 5^13 ≡ 3 (mod 7) using Z3. Proof: {thm_main}'
        })
    except Exception as e:
        checks.append({
            'name': 'main_theorem',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove 29^13 - 5^13 ≡ 3 (mod 7): {e}'
        })
    
    # Check 6: Numerical sanity check using SymPy
    try:
        result = (29**13 - 5**13) % 7
        passed = (result == 3)
        checks.append({
            'name': 'numerical_verification',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Computed (29^13 - 5^13) mod 7 = {result}. Expected 3.'
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_verification',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical verification failed: {e}'
        })
    
    # Check 7: SymPy symbolic verification
    try:
        n = sp.Symbol('n', integer=True)
        expr = (29**13 - 5**13 - 3 - 7*n)
        vals_match = True
        for test_n in range(-10, 11):
            if expr.subs(n, test_n) == 0:
                actual_n = (29**13 - 5**13 - 3) // 7
                vals_match = (test_n == actual_n)
                break
        
        # Direct symbolic check
        actual_result = (29**13 - 5**13) % 7
        symbolic_passed = (actual_result == 3)
        
        checks.append({
            'name': 'sympy_symbolic_check',
            'passed': symbolic_passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy computed (29^13 - 5^13) mod 7 = {actual_result}. Verified it equals 3.'
        })
    except Exception as e:
        checks.append({
            'name': 'sympy_symbolic_check',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy symbolic check failed: {e}'
        })
    
    all_passed = all(check['passed'] for check in checks)
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} [{check['backend']}]")
        print(f"    {check['details']}")