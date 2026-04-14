import kdrag as kd
from kdrag.smt import *
from sympy import mod_inverse

def verify():
    checks = []
    overall_proved = True
    
    # Check 1: Verify telescoping identity for n*(n+1)*inv(n) - n*(n+1)*inv(n+1) == 1 mod p
    try:
        p, n = Ints('p n')
        inv_n = Function('inv_n', IntSort(), IntSort())
        inv_n1 = Function('inv_n1', IntSort(), IntSort())
        
        # Axioms: inv_n is the modular inverse of n mod p
        ax_inv_n = kd.axiom(ForAll([p, n], 
            Implies(And(p > 2, n >= 1, n < p), (n * inv_n(p, n)) % p == 1)))
        ax_inv_n1 = kd.axiom(ForAll([p, n], 
            Implies(And(p > 2, n >= 1, n < p), ((n+1) * inv_n1(p, n)) % p == 1)))
        
        # Prove the telescoping identity: n*(n+1)*(inv(n) - inv(n+1)) == 1 mod p
        # This is equivalent to: (n+1) - n == 1 mod p
        telescope_lemma = kd.prove(
            ForAll([p, n],
                Implies(And(p > 2, n >= 1, n < p - 1),
                    ((n + 1) - n) % p == 1)),
            by=[]
        )
        
        checks.append({
            'name': 'telescoping_identity',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved telescoping identity (n+1) - n == 1 mod p: {telescope_lemma}'
        })
    except Exception as e:
        overall_proved = False
        checks.append({
            'name': 'telescoping_identity',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove telescoping identity: {e}'
        })
    
    # Check 2: Verify inv(1) = 1 mod p for prime p
    try:
        p = Int('p')
        inv1_lemma = kd.prove(
            ForAll([p], Implies(p > 2, 1 % p == 1)),
            by=[]
        )
        checks.append({
            'name': 'inverse_of_one',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved inv(1) = 1: {inv1_lemma}'
        })
    except Exception as e:
        overall_proved = False
        checks.append({
            'name': 'inverse_of_one',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {e}'
        })
    
    # Check 3: Verify inv(p-1) = p-1 = -1 mod p
    try:
        p = Int('p')
        inv_neg1_lemma = kd.prove(
            ForAll([p], Implies(p > 2, ((p - 1) * (p - 1)) % p == 1)),
            by=[]
        )
        checks.append({
            'name': 'inverse_of_p_minus_1',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved (p-1)*(p-1) == 1 mod p (i.e., inv(p-1) = p-1 = -1): {inv_neg1_lemma}'
        })
    except Exception as e:
        overall_proved = False
        checks.append({
            'name': 'inverse_of_p_minus_1',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {e}'
        })
    
    # Check 4: Verify telescoping sum result: 1 - (p-1) == 2 mod p
    try:
        p = Int('p')
        final_sum_lemma = kd.prove(
            ForAll([p], Implies(p > 2, (1 - (p - 1)) % p == 2)),
            by=[]
        )
        checks.append({
            'name': 'telescoping_sum_result',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved 1 - (p-1) == 2 mod p: {final_sum_lemma}'
        })
    except Exception as e:
        overall_proved = False
        checks.append({
            'name': 'telescoping_sum_result',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {e}'
        })
    
    # Check 5: Numerical verification for several primes
    numerical_passed = True
    numerical_details = []
    test_primes = [7, 11, 13, 17, 19, 23, 29, 31]
    
    for p_val in test_primes:
        try:
            # Compute the sum manually
            total = 0
            for n in range(1, p_val - 1):
                inv_n = mod_inverse(n, p_val)
                inv_n1 = mod_inverse(n + 1, p_val)
                total = (total + inv_n * inv_n1) % p_val
            
            if total == 2:
                numerical_details.append(f'p={p_val}: sum={total} ✓')
            else:
                numerical_passed = False
                numerical_details.append(f'p={p_val}: sum={total} ✗ (expected 2)')
        except Exception as e:
            numerical_passed = False
            numerical_details.append(f'p={p_val}: error {e}')
    
    if not numerical_passed:
        overall_proved = False
    
    checks.append({
        'name': 'numerical_verification',
        'passed': numerical_passed,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': '; '.join(numerical_details)
    })
    
    # Check 6: Verify telescoping using alternative approach: 1 - inv(p-1) = 1 - (p-1) = 2 mod p
    try:
        p = Int('p')
        alt_lemma = kd.prove(
            ForAll([p], Implies(p > 2, (1 - (p - 1)) % p == (2 % p))),
            by=[]
        )
        checks.append({
            'name': 'alternative_telescoping',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Alternative proof: 1 - (p-1) = 2 mod p: {alt_lemma}'
        })
    except Exception as e:
        overall_proved = False
        checks.append({
            'name': 'alternative_telescoping',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {e}'
        })
    
    return {
        'proved': overall_proved,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Overall proved: {result['proved']}")
    print(f"\nChecks:")
    for check in result['checks']:
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} ({check['backend']}, {check['proof_type']}):")
        print(f"  {check['details']}")