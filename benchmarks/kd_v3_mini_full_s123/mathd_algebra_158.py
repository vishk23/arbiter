import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified theorem in kdrag/Z3.
    # Let a be the smallest of the 5 consecutive even integers.
    # Their sum is a + (a+2) + (a+4) + (a+6) + (a+8) = 5a + 20.
    # The sum of the first 8 odd counting numbers is 64, so being 4 less means 60.
    # We prove that the equation 5a + 20 = 60 forces a = 8.
    a = Int('a')
    thm_name = 'smallest_even_integer_is_8'
    try:
        thm = kd.prove(ForAll([a], Implies(5 * a + 20 == 60, a == 8)))
        checks.append({
            'name': thm_name,
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved by Z3: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': thm_name,
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove the main implication in kdrag: {e}'
        })

    # Check 2: Verified symbolic calculation in SymPy for the sum of the first 8 odd numbers.
    # This is exact arithmetic, not numerical approximation.
    sym_name = 'sum_first_8_odds_is_64'
    try:
        odd_sum = sp.Integer(1) + sp.Integer(3) + sp.Integer(5) + sp.Integer(7) + sp.Integer(9) + sp.Integer(11) + sp.Integer(13) + sp.Integer(15)
        passed = (sp.simplify(odd_sum - 64) == 0)
        checks.append({
            'name': sym_name,
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'Exact symbolic sum computed by SymPy: {odd_sum}.'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': sym_name,
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'SymPy failed to compute the odd sum: {e}'
        })

    # Check 3: Numerical sanity check at the concrete solution a = 8.
    num_name = 'sanity_check_at_a_equals_8'
    try:
        a_val = 8
        even_sum = a_val + (a_val + 2) + (a_val + 4) + (a_val + 6) + (a_val + 8)
        odd_sum = sum([1, 3, 5, 7, 9, 11, 13, 15])
        passed = (even_sum == odd_sum - 4) and (a_val == 8)
        checks.append({
            'name': num_name,
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'For a=8, even_sum={even_sum}, odd_sum={odd_sum}, and even_sum == odd_sum - 4 is {passed}.'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': num_name,
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical sanity check failed: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)