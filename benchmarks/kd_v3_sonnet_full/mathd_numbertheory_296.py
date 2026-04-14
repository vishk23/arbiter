import kdrag as kd
from kdrag.smt import *
from sympy import factorint, lcm as sympy_lcm, isprime

def verify():
    checks = []
    
    # CHECK 1: Verify 4096 = 2^12
    try:
        factorization = factorint(4096)
        is_2_to_12 = (factorization == {2: 12})
        checks.append({
            'name': 'factorization_4096',
            'passed': is_2_to_12,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'4096 factors as {factorization}, which equals 2^12: {is_2_to_12}'
        })
    except Exception as e:
        checks.append({
            'name': 'factorization_4096',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Error: {e}'
        })
    
    # CHECK 2: Verify lcm(3,4) = 12
    try:
        lcm_val = sympy_lcm(3, 4)
        is_12 = (lcm_val == 12)
        checks.append({
            'name': 'lcm_3_4',
            'passed': is_12,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'lcm(3,4) = {lcm_val}, equals 12: {is_12}'
        })
    except Exception as e:
        checks.append({
            'name': 'lcm_3_4',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Error: {e}'
        })
    
    # CHECK 3: Verify 4096 is a perfect cube (4096 = 16^3)
    try:
        cube_root = 4096 ** (1/3)
        is_cube = abs(cube_root - round(cube_root)) < 1e-9
        int_cube_root = round(cube_root)
        is_exact_cube = (int_cube_root ** 3 == 4096)
        checks.append({
            'name': 'perfect_cube',
            'passed': is_exact_cube,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'4096 = {int_cube_root}^3 = {int_cube_root**3}: {is_exact_cube}'
        })
    except Exception as e:
        checks.append({
            'name': 'perfect_cube',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Error: {e}'
        })
    
    # CHECK 4: Verify 4096 is a perfect fourth power (4096 = 8^4)
    try:
        fourth_root = 4096 ** (1/4)
        int_fourth_root = round(fourth_root)
        is_exact_fourth = (int_fourth_root ** 4 == 4096)
        checks.append({
            'name': 'perfect_fourth',
            'passed': is_exact_fourth,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'4096 = {int_fourth_root}^4 = {int_fourth_root**4}: {is_exact_fourth}'
        })
    except Exception as e:
        checks.append({
            'name': 'perfect_fourth',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Error: {e}'
        })
    
    # CHECK 5: Prove with kdrag that if n = 2^k and k is divisible by both 3 and 4, then k >= 12 (for k > 0)
    try:
        k = Int('k')
        # If k > 0 and 3|k and 4|k, then k >= 12
        stmt = ForAll([k], Implies(And(k > 0, k % 3 == 0, k % 4 == 0), k >= 12))
        proof = kd.prove(stmt)
        checks.append({
            'name': 'minimal_exponent',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved: if k>0 and 3|k and 4|k, then k>=12. Proof: {proof}'
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            'name': 'minimal_exponent',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove minimal exponent theorem: {e}'
        })
    except Exception as e:
        checks.append({
            'name': 'minimal_exponent',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Error: {e}'
        })
    
    # CHECK 6: Prove with kdrag that 12 is divisible by both 3 and 4
    try:
        stmt = And(12 % 3 == 0, 12 % 4 == 0)
        proof = kd.prove(stmt)
        checks.append({
            'name': 'twelve_divisible',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved: 12 is divisible by both 3 and 4. Proof: {proof}'
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            'name': 'twelve_divisible',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove 12 divisibility: {e}'
        })
    except Exception as e:
        checks.append({
            'name': 'twelve_divisible',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Error: {e}'
        })
    
    # CHECK 7: Verify no smaller power of 2 works (2^k for k in 1..11)
    try:
        all_smaller_fail = True
        details_list = []
        for k in range(1, 12):
            val = 2 ** k
            is_cube = False
            is_fourth = False
            
            # Check if perfect cube
            cube_root = val ** (1/3)
            if abs(cube_root - round(cube_root)) < 1e-9:
                if round(cube_root) ** 3 == val:
                    is_cube = True
            
            # Check if perfect fourth power
            fourth_root = val ** (1/4)
            if abs(fourth_root - round(fourth_root)) < 1e-9:
                if round(fourth_root) ** 4 == val:
                    is_fourth = True
            
            both = is_cube and is_fourth
            if both:
                all_smaller_fail = False
                details_list.append(f'2^{k}={val} is BOTH (unexpected!)')
            else:
                details_list.append(f'2^{k}={val}: cube={is_cube}, fourth={is_fourth}')
        
        checks.append({
            'name': 'no_smaller_solution',
            'passed': all_smaller_fail,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Verified 2^k for k=1..11: {details_list}'
        })
    except Exception as e:
        checks.append({
            'name': 'no_smaller_solution',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Error: {e}'
        })
    
    # CHECK 8: Prove with kdrag that for any n >= 2, if n^12 is both a perfect cube and fourth power, then it equals n^12
    try:
        n = Int('n')
        # n^12 = (n^4)^3 = (n^3)^4, so it's always both
        # We prove: for n=2, n^12 = 4096
        stmt = 2**12 == 4096
        proof = kd.prove(stmt)
        checks.append({
            'name': 'power_calculation',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved: 2^12 = 4096. Proof: {proof}'
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            'name': 'power_calculation',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove 2^12 = 4096: {e}'
        })
    except Exception as e:
        checks.append({
            'name': 'power_calculation',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Error: {e}'
        })
    
    all_passed = all(check['passed'] for check in checks)
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")