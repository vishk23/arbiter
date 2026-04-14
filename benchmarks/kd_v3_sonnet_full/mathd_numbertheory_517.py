import kdrag as kd
from kdrag.smt import *
from sympy import factorint

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Direct Z3 proof that 121*122*123 mod 4 = 2
    try:
        x = Int('x')
        product_mod = kd.prove(
            (121 * 122 * 123) % 4 == 2
        )
        checks.append({
            'name': 'direct_modular_arithmetic',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 proved 121*122*123 mod 4 = 2 directly. Proof object: {product_mod}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'direct_modular_arithmetic',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove directly: {e}'
        })
    
    # Check 2: Prove congruence reduction 121 ≡ 1 (mod 4)
    try:
        thm1 = kd.prove(121 % 4 == 1)
        checks.append({
            'name': 'congruence_121_mod_4',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 proved 121 ≡ 1 (mod 4). Proof: {thm1}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'congruence_121_mod_4',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {e}'
        })
    
    # Check 3: Prove congruence reduction 122 ≡ 2 (mod 4)
    try:
        thm2 = kd.prove(122 % 4 == 2)
        checks.append({
            'name': 'congruence_122_mod_4',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 proved 122 ≡ 2 (mod 4). Proof: {thm2}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'congruence_122_mod_4',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {e}'
        })
    
    # Check 4: Prove congruence reduction 123 ≡ 3 (mod 4)
    try:
        thm3 = kd.prove(123 % 4 == 3)
        checks.append({
            'name': 'congruence_123_mod_4',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 proved 123 ≡ 3 (mod 4). Proof: {thm3}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'congruence_123_mod_4',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {e}'
        })
    
    # Check 5: Prove 1*2*3 mod 4 = 6 mod 4 = 2
    try:
        thm_reduced = kd.prove((1 * 2 * 3) % 4 == 2)
        checks.append({
            'name': 'reduced_product_mod_4',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 proved 1*2*3 mod 4 = 2. Proof: {thm_reduced}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'reduced_product_mod_4',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {e}'
        })
    
    # Check 6: Prove general modular property: (a mod m)*(b mod m) ≡ (a*b) (mod m)
    try:
        a, b, m = Ints('a b m')
        mod_mult_thm = kd.prove(
            ForAll([a, b, m],
                Implies(m > 0,
                    ((a % m) * (b % m)) % m == (a * b) % m))
        )
        checks.append({
            'name': 'modular_multiplication_property',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 proved general modular multiplication property. Proof: {mod_mult_thm}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'modular_multiplication_property',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {e}'
        })
    
    # Check 7: Numerical sanity check
    try:
        computed = (121 * 122 * 123) % 4
        expected = 2
        passed = (computed == expected)
        checks.append({
            'name': 'numerical_verification',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Computed 121*122*123 mod 4 = {computed}, expected {expected}'
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
            'details': f'Numerical check failed: {e}'
        })
    
    # Check 8: Verify actual product value and factorization
    try:
        actual_product = 121 * 122 * 123
        residue = actual_product % 4
        factors = factorint(actual_product)
        checks.append({
            'name': 'product_factorization',
            'passed': residue == 2,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Product = {actual_product}, residue = {residue}, factorization = {factors}'
        })
        if residue != 2:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'product_factorization',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Factorization check failed: {e}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])}):\n")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} [{check['backend']}]")
        print(f"  {check['details']}")
        print()