import kdrag as kd
from kdrag.smt import *
from sympy import gcd as sympy_gcd, lcm as sympy_lcm

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Verify the GCD-LCM identity theorem using kdrag
    try:
        a, b = Ints('a b')
        gcd_func = Function('gcd', IntSort(), IntSort(), IntSort())
        lcm_func = Function('lcm', IntSort(), IntSort(), IntSort())
        
        # Axiom: gcd(a,b) * lcm(a,b) = a * b
        gcd_lcm_identity = axiom(ForAll([a, b], 
            Implies(And(a > 0, b > 0), 
                    gcd_func(a, b) * lcm_func(a, b) == a * b)))
        
        # Specific instance: gcd(n, 40) = 10 and lcm(n, 40) = 280
        n = Int('n')
        hypothesis = And(n > 0, gcd_func(n, 40) == 10, lcm_func(n, 40) == 280)
        
        # Prove n = 70 from the identity
        thm = prove(ForAll([n], Implies(hypothesis, n == 70)), by=[gcd_lcm_identity])
        
        checks.append({
            'name': 'gcd_lcm_identity_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved using GCD-LCM identity: gcd(n,40)*lcm(n,40) = n*40, so 10*280 = n*40, thus n = 70. Proof object: {thm}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'gcd_lcm_identity_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove using GCD-LCM identity: {str(e)}'
        })
    
    # Check 2: Direct algebraic proof that n = 70 satisfies constraints
    try:
        n = Int('n')
        # Using Z3's built-in gcd and lcm would be ideal, but we prove arithmetically
        # If gcd(n, 40) = 10 and lcm(n, 40) = 280, then by identity: 10 * 280 = n * 40
        constraint = (10 * 280 == n * 40)
        solution_thm = prove(ForAll([n], Implies(constraint, n == 70)))
        
        checks.append({
            'name': 'algebraic_solution',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved n = 70 from equation 10*280 = n*40. Proof: {solution_thm}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'algebraic_solution',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed algebraic proof: {str(e)}'
        })
    
    # Check 3: Verify n=70 satisfies gcd(70, 40) = 10 using SymPy
    try:
        gcd_result = sympy_gcd(70, 40)
        gcd_check = (gcd_result == 10)
        
        checks.append({
            'name': 'sympy_gcd_verification',
            'passed': gcd_check,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy computed gcd(70, 40) = {gcd_result}, expected 10: {gcd_check}'
        })
        all_passed = all_passed and gcd_check
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'sympy_gcd_verification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy gcd verification failed: {str(e)}'
        })
    
    # Check 4: Verify n=70 satisfies lcm(70, 40) = 280 using SymPy
    try:
        lcm_result = sympy_lcm(70, 40)
        lcm_check = (lcm_result == 280)
        
        checks.append({
            'name': 'sympy_lcm_verification',
            'passed': lcm_check,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy computed lcm(70, 40) = {lcm_result}, expected 280: {lcm_check}'
        })
        all_passed = all_passed and lcm_check
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'sympy_lcm_verification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy lcm verification failed: {str(e)}'
        })
    
    # Check 5: Numerical sanity check - verify the identity holds
    try:
        gcd_val = 10
        lcm_val = 280
        n_val = 70
        b_val = 40
        
        identity_holds = (gcd_val * lcm_val == n_val * b_val)
        
        checks.append({
            'name': 'numerical_identity_check',
            'passed': identity_holds,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Verified gcd*lcm = n*b: {gcd_val}*{lcm_val} = {n_val}*{b_val} = {gcd_val * lcm_val}: {identity_holds}'
        })
        all_passed = all_passed and identity_holds
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerical_identity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical verification failed: {str(e)}'
        })
    
    # Check 6: Verify uniqueness - no other positive n satisfies both constraints
    try:
        n = Int('n')
        # For any n where gcd(n,40)=10 and lcm(n,40)=280, we have n*40 = 10*280 = 2800
        uniqueness = prove(ForAll([n], 
            Implies(And(n > 0, n * 40 == 2800), n == 70)))
        
        checks.append({
            'name': 'uniqueness_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved uniqueness: if n*40 = 2800 and n > 0, then n = 70. Proof: {uniqueness}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'uniqueness_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed uniqueness proof: {str(e)}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proof status: {'PROVED' if result['proved'] else 'FAILED'}")
    print(f"\nCheck results:")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"      {check['details']}")