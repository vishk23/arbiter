import kdrag as kd
from kdrag.smt import *
import sympy as sp

def verify():
    checks = []
    all_passed = True
    
    # Check 1: kdrag proof that a=5 is the unique positive solution
    try:
        a = Int('a')
        # Product equals 8*sum: a(a-1)(a+1) = 8*3a = 24a
        # Simplifies to: (a-1)(a+1) = 24, i.e., a^2 - 1 = 24, i.e., a^2 = 25
        # For positive integers, a = 5
        thm1 = kd.prove(Implies(And(a > 0, a*(a-1)*(a+1) == 24*a), a == 5))
        checks.append({
            'name': 'unique_solution_a5',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 proof that a=5 is the unique positive solution: {thm1}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'unique_solution_a5',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove a=5: {e}'
        })
    
    # Check 2: kdrag proof that product condition holds for a=5
    try:
        thm2 = kd.prove(4*5*6 == 8*(4+5+6))
        checks.append({
            'name': 'product_equals_8times_sum',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 proof that 4*5*6 = 8*(4+5+6): {thm2}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'product_equals_8times_sum',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove product condition: {e}'
        })
    
    # Check 3: kdrag proof that sum of squares is 77
    try:
        thm3 = kd.prove(4*4 + 5*5 + 6*6 == 77)
        checks.append({
            'name': 'sum_of_squares_77',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 proof that 4^2 + 5^2 + 6^2 = 77: {thm3}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'sum_of_squares_77',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove sum of squares: {e}'
        })
    
    # Check 4: kdrag proof of algebraic constraint (a^2 = 25 from product condition)
    try:
        a = Int('a')
        # From a(a-1)(a+1) = 24a with a > 0, we get (a-1)(a+1) = 24
        # Which expands to a^2 - 1 = 24, so a^2 = 25
        thm4 = kd.prove(ForAll([a], Implies(And(a > 0, (a-1)*(a+1) == 24), a*a == 25)))
        checks.append({
            'name': 'algebraic_constraint',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 proof that (a-1)(a+1)=24 implies a^2=25: {thm4}'
        })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'algebraic_constraint',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove algebraic constraint: {e}'
        })
    
    # Check 5: SymPy symbolic verification
    try:
        a_sym = sp.Symbol('a', positive=True, integer=True)
        # Solve a(a-1)(a+1) = 8*3a for a > 0
        eq = sp.Eq(a_sym*(a_sym-1)*(a_sym+1), 24*a_sym)
        solutions = sp.solve(eq, a_sym)
        positive_sols = [s for s in solutions if s.is_positive]
        if len(positive_sols) == 1 and positive_sols[0] == 5:
            sum_of_squares = 4**2 + 5**2 + 6**2
            if sum_of_squares == 77:
                checks.append({
                    'name': 'sympy_symbolic_verification',
                    'passed': True,
                    'backend': 'sympy',
                    'proof_type': 'symbolic_zero',
                    'details': f'SymPy confirms unique solution a=5, sum of squares = {sum_of_squares}'
                })
            else:
                all_passed = False
                checks.append({
                    'name': 'sympy_symbolic_verification',
                    'passed': False,
                    'backend': 'sympy',
                    'proof_type': 'symbolic_zero',
                    'details': f'Sum of squares computed as {sum_of_squares}, expected 77'
                })
        else:
            all_passed = False
            checks.append({
                'name': 'sympy_symbolic_verification',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'SymPy found solutions {positive_sols}, expected [5]'
            })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'sympy_symbolic_verification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy verification failed: {e}'
        })
    
    # Check 6: Numerical sanity check
    try:
        product = 4 * 5 * 6
        sum_val = 4 + 5 + 6
        eight_times_sum = 8 * sum_val
        sum_of_squares = 4**2 + 5**2 + 6**2
        
        if product == eight_times_sum and product == 120 and sum_of_squares == 77:
            checks.append({
                'name': 'numerical_sanity_check',
                'passed': True,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'Numerical check: 4*5*6={product}, 8*(4+5+6)={eight_times_sum}, 4^2+5^2+6^2={sum_of_squares}'
            })
        else:
            all_passed = False
            checks.append({
                'name': 'numerical_sanity_check',
                'passed': False,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'Numerical mismatch: product={product}, 8*sum={eight_times_sum}, squares_sum={sum_of_squares}'
            })
    except Exception as e:
        all_passed = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })
    
    return {
        'proved': all_passed,
        'checks': checks
    }

if __name__ == '__main__':
    result = verify()
    print(f"Proved: {result['proved']}")
    for check in result['checks']:
        status = 'PASS' if check['passed'] else 'FAIL'
        print(f"[{status}] {check['name']} ({check['backend']}/{check['proof_type']})")
        print(f"  {check['details']}")