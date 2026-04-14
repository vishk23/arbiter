import kdrag as kd
from kdrag.smt import *
from sympy import symbols as sp_symbols, minimal_polynomial, Integer as sp_Integer

def verify():
    checks = []
    all_passed = True
    
    # Check 1: Prove the divisibility rule for 11 using kdrag
    try:
        a, b, c, d = Ints('a b c d')
        num = Function('num', IntSort(), IntSort(), IntSort(), IntSort(), IntSort())
        num = kd.define('num', [a, b, c, d], 1000*a + 100*b + 10*c + d)
        alt_sum = Function('alt_sum', IntSort(), IntSort(), IntSort(), IntSort(), IntSort())
        alt_sum = kd.define('alt_sum', [a, b, c, d], a - b + c - d)
        
        # Prove that if alt_sum is divisible by 11, then num is divisible by 11
        # For the specific case 20A7: alt_sum = 2 - 0 + A - 7 = A - 5
        A = Int('A')
        specific_alt = kd.prove(
            ForAll([A], 
                Implies(
                    And(A >= 0, A <= 9),
                    alt_sum(2, 0, A, 7) == A - 5
                )),
            by=[alt_sum.defn]
        )
        
        checks.append({
            'name': 'alternating_sum_formula',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved alt_sum(2,0,A,7) = A-5 using kdrag: {specific_alt}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'alternating_sum_formula',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 2: Prove A=5 is the unique single digit solution
    try:
        A = Int('A')
        # For A-5 to be divisible by 11 with A in [0,9], we need A-5 = 0
        unique_sol = kd.prove(
            ForAll([A],
                Implies(
                    And(A >= 0, A <= 9, (A - 5) % 11 == 0),
                    A == 5
                )
            )
        )
        
        checks.append({
            'name': 'unique_digit_solution',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved A=5 is unique digit with (A-5) divisible by 11: {unique_sol}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'unique_digit_solution',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 3: Verify 2057 is divisible by 11 (numerical)
    try:
        result = 2057 % 11
        passed = (result == 0)
        checks.append({
            'name': 'numerical_verification_2057',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'2057 mod 11 = {result}, divisible: {passed}'
        })
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerical_verification_2057',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 4: Verify other digits don't work (numerical)
    try:
        other_digits_fail = True
        details_list = []
        for digit in range(10):
            if digit == 5:
                continue
            num = 2000 + 10*digit + 7
            if num % 11 == 0:
                other_digits_fail = False
                details_list.append(f'{digit}: {num} is divisible by 11 (unexpected)')
            else:
                details_list.append(f'{digit}: {num} mod 11 = {num % 11}')
        
        checks.append({
            'name': 'other_digits_not_solutions',
            'passed': other_digits_fail,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': '; '.join(details_list)
        })
        if not other_digits_fail:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'other_digits_not_solutions',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 5: Symbolic verification using SymPy
    try:
        A_sym = sp_symbols('A', integer=True)
        # For a single digit, A-5 must be 0 for divisibility by 11
        expr = A_sym - 5
        # Verify that when A=5, expr=0
        val_at_5 = expr.subs(A_sym, 5)
        passed = (val_at_5 == 0)
        
        checks.append({
            'name': 'symbolic_zero_at_A_equals_5',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Alternating sum A-5 equals {val_at_5} when A=5'
        })
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'symbolic_zero_at_A_equals_5',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed: {str(e)}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print('VERIFICATION RESULT:')
    print(f"Proved: {result['proved']}")
    print(f"\nChecks ({len(result['checks'])} total):")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"  [{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"        {check['details']}")
    print(f"\nConclusion: The digit that makes 20_7 divisible by 11 is 5.")
    print(f"Overall verification: {'SUCCESS' if result['proved'] else 'FAILED'}")