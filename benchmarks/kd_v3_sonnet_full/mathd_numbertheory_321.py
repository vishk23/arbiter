import kdrag as kd
from kdrag.smt import *
from sympy import mod_inverse as sympy_mod_inverse

def verify() -> dict:
    checks = []
    all_passed = True
    
    # Check 1: Verify 35*40 = 1400 using kdrag
    try:
        product_thm = kd.prove(35 * 40 == 1400)
        checks.append({
            'name': 'product_check',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved 35*40 = 1400 using Z3 (certified proof object returned)'
        })
    except Exception as e:
        checks.append({
            'name': 'product_check',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove 35*40 = 1400: {str(e)}'
        })
        all_passed = False
    
    # Check 2: Verify 35*40 ≡ 1 (mod 1399) using kdrag
    try:
        thm_mod = kd.prove((35 * 40) % 1399 == 1)
        checks.append({
            'name': 'inverse_35_40',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved 35*40 ≡ 1 (mod 1399) using Z3 (certified proof)'
        })
    except Exception as e:
        checks.append({
            'name': 'inverse_35_40',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove 35*40 ≡ 1 (mod 1399): {str(e)}'
        })
        all_passed = False
    
    # Check 3: Verify 160 ≡ 4*40 (mod 1399) using kdrag
    try:
        thm_equiv = kd.prove(160 % 1399 == (4 * 40) % 1399)
        checks.append({
            'name': 'equiv_160_4times40',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved 160 ≡ 4*40 (mod 1399) using Z3'
        })
    except Exception as e:
        checks.append({
            'name': 'equiv_160_4times40',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove 160 ≡ 4*40 (mod 1399): {str(e)}'
        })
        all_passed = False
    
    # Check 4: Verify 1058 ≡ 4*35*4*35*2 (mod 1399) - construction check
    try:
        thm_construction = kd.prove(1058 % 1399 == (4 * 35 * 4 * 35 * 2) % 1399)
        checks.append({
            'name': 'construction_1058',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved 1058 ≡ 4*35*4*35*2 (mod 1399) using Z3'
        })
    except Exception as e:
        checks.append({
            'name': 'construction_1058',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed construction check: {str(e)}'
        })
        all_passed = False
    
    # Check 5: MAIN PROOF - Verify 160*1058 ≡ 1 (mod 1399) using kdrag
    try:
        main_thm = kd.prove((160 * 1058) % 1399 == 1)
        checks.append({
            'name': 'main_inverse_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'MAIN PROOF: Proved 160*1058 ≡ 1 (mod 1399) using Z3 - certified that 1058 is the multiplicative inverse of 160 mod 1399'
        })
    except Exception as e:
        checks.append({
            'name': 'main_inverse_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'MAIN PROOF FAILED: {str(e)}'
        })
        all_passed = False
    
    # Check 6: Verify 0 <= 1058 < 1399 (range constraint) using kdrag
    try:
        range_thm = kd.prove(And(1058 >= 0, 1058 < 1399))
        checks.append({
            'name': 'range_check',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved 0 <= 1058 < 1399 using Z3'
        })
    except Exception as e:
        checks.append({
            'name': 'range_check',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed range check: {str(e)}'
        })
        all_passed = False
    
    # Check 7: Numerical sanity check using SymPy
    try:
        sympy_result = sympy_mod_inverse(160, 1399)
        numerical_passed = (sympy_result == 1058)
        checks.append({
            'name': 'numerical_sanity',
            'passed': numerical_passed,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'SymPy mod_inverse(160, 1399) = {sympy_result}, expected 1058'
        })
        if not numerical_passed:
            all_passed = False
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'SymPy numerical check failed: {str(e)}'
        })
        all_passed = False
    
    # Check 8: Direct computation sanity check
    try:
        direct_check = ((160 * 1058) % 1399 == 1)
        checks.append({
            'name': 'direct_computation',
            'passed': direct_check,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Direct Python computation: (160*1058) % 1399 = {(160*1058) % 1399}'
        })
        if not direct_check:
            all_passed = False
    except Exception as e:
        checks.append({
            'name': 'direct_computation',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Direct computation failed: {str(e)}'
        })
        all_passed = False
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"  {status} {check['name']} [{check['backend']}/{check['proof_type']}]")
        print(f"    {check['details']}")