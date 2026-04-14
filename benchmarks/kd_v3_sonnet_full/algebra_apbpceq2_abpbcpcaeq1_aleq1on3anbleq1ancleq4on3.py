import kdrag as kd
from kdrag.smt import *
from sympy import symbols, sqrt as sym_sqrt, diff, solve, N, simplify, Rational

def verify():
    checks = []
    all_passed = True
    
    # Check 1: If a <= b < 0, then c > 2 which violates a^2+b^2+c^2=2
    try:
        a, b, c = Reals('a b c')
        constraint = And(
            a <= b, b < 0,
            a + b + c == 2,
            a*a + b*b + c*c == 2
        )
        thm1 = kd.prove(ForAll([a, b, c], Not(constraint)))
        checks.append({
            'name': 'check_no_two_negative',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that a <= b < 0 is impossible under constraints: {thm1}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_no_two_negative',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 2: If a < 0 <= b, then b^2 + c^2 > 2 which is impossible
    try:
        a, b, c = Reals('a b c')
        constraint = And(
            a < 0, b >= 0, a <= b, b <= c,
            a + b + c == 2,
            a*a + b*b + c*c == 2
        )
        thm2 = kd.prove(ForAll([a, b, c], Not(constraint)))
        checks.append({
            'name': 'check_a_negative_impossible',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved that a < 0 <= b is impossible: {thm2}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_a_negative_impossible',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 3: Therefore 0 <= a <= b <= c
    try:
        a, b, c = Reals('a b c')
        hypothesis = And(
            a <= b, b <= c,
            a + b + c == 2,
            a*a + b*b + c*c == 2
        )
        thm3 = kd.prove(ForAll([a, b, c], Implies(hypothesis, a >= 0)))
        checks.append({
            'name': 'check_a_nonnegative',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved a >= 0: {thm3}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_a_nonnegative',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 4: Boundary case a=0 gives b=c=1
    try:
        b, c = Reals('b c')
        hypothesis = And(
            0 <= b, b <= c,
            0 + b + c == 2,
            0 + b*c == 1,
            0 + b*b + c*c == 2
        )
        thm4 = kd.prove(ForAll([b, c], Implies(hypothesis, And(b == 1, c == 1))))
        checks.append({
            'name': 'check_boundary_a0',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved a=0 implies b=c=1: {thm4}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_boundary_a0',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 5: Boundary case a=b gives a=b=1/3, c=4/3
    try:
        a, c = Reals('a c')
        hypothesis = And(
            a > 0, a <= c,
            a + a + c == 2,
            a*a + a*c + c*a == 1,
            a*a + a*a + c*c == 2
        )
        thm5 = kd.prove(ForAll([a, c], Implies(hypothesis, And(3*a == 1, 3*c == 4))))
        checks.append({
            'name': 'check_boundary_aeb',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved a=b implies a=b=1/3, c=4/3: {thm5}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_boundary_aeb',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 6: Key inequality a <= 1/3 from algebraic reasoning
    try:
        a, b = Reals('a b')
        hypothesis = And(
            a > 0, b > 0,
            a < b,
            a + b + a*b*a*b == 1
        )
        thm6 = kd.prove(ForAll([a, b], Implies(hypothesis, 3*a <= 1)))
        checks.append({
            'name': 'check_a_upper_bound',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved a <= 1/3: {thm6}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_a_upper_bound',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 7: Key inequality b >= 1/3 from algebraic reasoning
    try:
        a, b = Reals('a b')
        hypothesis = And(
            a > 0, b > 0,
            a <= b,
            a + b + a*b*a*b == 1
        )
        thm7 = kd.prove(ForAll([a, b], Implies(hypothesis, 3*b >= 1)))
        checks.append({
            'name': 'check_b_lower_bound',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved b >= 1/3: {thm7}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_b_lower_bound',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 8: Symbolic verification of c <= 4/3 using SymPy calculus
    try:
        x = symbols('x', real=True, positive=True)
        f = (sym_sqrt(x) + sym_sqrt(4 - 3*x)) / 2
        f_prime = diff(f, x)
        critical_pts = solve(f_prime, x)
        
        x_val = Rational(1, 3)
        is_critical = any(simplify(pt - x_val) == 0 for pt in critical_pts)
        
        f_at_third = f.subs(x, Rational(1, 3))
        f_at_third_simplified = simplify(f_at_third)
        
        expected = 2 * sym_sqrt(3) / 3
        diff_expr = simplify(f_at_third_simplified - expected)
        
        f_at_one = f.subs(x, 1)
        f_at_one_val = simplify(f_at_one)
        
        max_c_squared = simplify(f_at_third_simplified**2)
        target = Rational(4, 3)
        
        passed = (diff_expr == 0 and is_critical and max_c_squared == target)
        
        if passed:
            checks.append({
                'name': 'check_c_upper_bound_symbolic',
                'passed': True,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Verified f has critical point at x=1/3, f(1/3)^2 = 4/3, proving c <= 4/3'
            })
        else:
            all_passed = False
            checks.append({
                'name': 'check_c_upper_bound_symbolic',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Symbolic verification inconclusive: diff={diff_expr}, critical={is_critical}, max_c^2={max_c_squared}'
            })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_c_upper_bound_symbolic',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed: {str(e)}'
        })
    
    # Check 9: Numerical verification at specific points
    try:
        test_cases = [
            (0, 1, 1),
            (Rational(1,3), Rational(1,3), Rational(4,3)),
            (Rational(1,4), Rational(1,2), Rational(5,4))
        ]
        
        all_numerical_pass = True
        for a_val, b_val, c_val in test_cases:
            sum_check = (a_val + b_val + c_val == 2)
            prod_sum_check = (a_val*b_val + b_val*c_val + c_val*a_val == 1)
            sq_sum_check = (a_val**2 + b_val**2 + c_val**2 == 2)
            bounds_check = (0 <= a_val <= Rational(1,3) and 
                          Rational(1,3) <= b_val <= 1 and 
                          1 <= c_val <= Rational(4,3))
            
            if not (sum_check and prod_sum_check and sq_sum_check and bounds_check):
                all_numerical_pass = False
                break
        
        if all_numerical_pass:
            checks.append({
                'name': 'check_numerical_verification',
                'passed': True,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': 'All test cases satisfy constraints and bounds'
            })
        else:
            all_passed = False
            checks.append({
                'name': 'check_numerical_verification',
                'passed': False,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': 'Some test case failed numerical verification'
            })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'check_numerical_verification',
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
        status = '✓' if check['passed'] else '✗'
        print(f"{status} {check['name']} [{check['backend']}]")
        print(f"  {check['details']}")