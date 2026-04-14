import kdrag as kd
from kdrag.smt import *
import sympy as sp
from typing import Dict, List, Any

def verify() -> Dict[str, Any]:
    checks = []
    all_passed = True
    
    # Check 1: Verify 2013 mod 9 = 6 (given example)
    try:
        b, n = Ints('b n')
        check1_thm = kd.prove(2013 % 9 == 6)
        checks.append({
            'name': 'base_9_example',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Verified 2013 mod 9 = 6: {check1_thm}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'base_9_example',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 2: Verify equivalence condition (n mod b = 3 iff (n-3) mod b = 0)
    try:
        b, n = Ints('b n')
        equiv_thm = kd.prove(ForAll([b, n], 
            Implies(b > 0, (n % b == 3) == ((n - 3) % b == 0))))
        checks.append({
            'name': 'remainder_equivalence',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved n mod b = 3 iff (n-3) mod b = 0: {equiv_thm}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'remainder_equivalence',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 3: Verify 2010 = 2013 - 3
    try:
        arith_thm = kd.prove(2013 - 3 == 2010)
        checks.append({
            'name': 'arithmetic_2010',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Verified 2013 - 3 = 2010: {arith_thm}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'arithmetic_2010',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 4: Verify prime factorization of 2010 using SymPy
    try:
        factorization = sp.factorint(2010)
        expected = {2: 1, 3: 1, 5: 1, 67: 1}
        sympy_passed = (factorization == expected)
        if sympy_passed:
            checks.append({
                'name': 'prime_factorization',
                'passed': True,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Verified 2010 = 2^1 * 3^1 * 5^1 * 67^1: {factorization}'
            })
        else:
            all_passed = False
            checks.append({
                'name': 'prime_factorization',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Factorization mismatch: got {factorization}, expected {expected}'
            })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'prime_factorization',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 5: Verify divisor count formula using SymPy
    try:
        num_divisors = sp.divisor_count(2010)
        expected_count = (1+1)*(1+1)*(1+1)*(1+1)
        divisor_passed = (num_divisors == expected_count == 16)
        if divisor_passed:
            checks.append({
                'name': 'divisor_count',
                'passed': True,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Verified 2010 has 16 divisors: {num_divisors}'
            })
        else:
            all_passed = False
            checks.append({
                'name': 'divisor_count',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Divisor count mismatch: got {num_divisors}, expected 16'
            })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'divisor_count',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 6: Verify divisors <= 3 using SymPy
    try:
        divisors = sp.divisors(2010)
        small_divisors = [d for d in divisors if d <= 3]
        small_div_passed = (small_divisors == [1, 2, 3])
        if small_div_passed:
            checks.append({
                'name': 'small_divisors',
                'passed': True,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Verified divisors of 2010 that are <= 3: {small_divisors}'
            })
        else:
            all_passed = False
            checks.append({
                'name': 'small_divisors',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Small divisors mismatch: got {small_divisors}, expected [1, 2, 3]'
            })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'small_divisors',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 7: Verify that b > 3 is required for digit 3 to be valid
    try:
        b = Int('b')
        digit_validity_thm = kd.prove(ForAll([b], Implies(And(b > 0, b <= 3), Not(3 < b))))
        checks.append({
            'name': 'digit_validity',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Verified b <= 3 implies digit 3 is invalid: {digit_validity_thm}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'digit_validity',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 8: Verify final answer 16 - 3 = 13
    try:
        final_thm = kd.prove(16 - 3 == 13)
        checks.append({
            'name': 'final_answer',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Verified 16 - 3 = 13: {final_thm}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'final_answer',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Numerical sanity check: verify some specific bases
    try:
        test_bases = [4, 5, 6, 10, 15, 30, 67, 2010]
        numerical_passed = True
        for base in test_bases:
            if 2010 % base == 0 and base > 3:
                if 2013 % base != 3:
                    numerical_passed = False
                    break
        
        if numerical_passed:
            checks.append({
                'name': 'numerical_sanity',
                'passed': True,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'Verified 2013 mod b = 3 for sample divisors of 2010 > 3: {test_bases}'
            })
        else:
            all_passed = False
            checks.append({
                'name': 'numerical_sanity',
                'passed': False,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': 'Numerical verification failed for some test bases'
            })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerical_sanity',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Failed: {str(e)}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']})")
        print(f"        {check['details']}")