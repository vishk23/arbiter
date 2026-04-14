import kdrag as kd
from kdrag.smt import *
from sympy import Integer, symbols


def verify():
    checks = []

    # Verified proof: derive the middle number from the sum of squares equation.
    n = Int('n')
    thm_middle = None
    try:
        thm_middle = kd.prove(
            ForAll([n],
                   Implies(And(n >= 0,
                               3*n*n + 8 == 12296),
                           n == 64))
        )
        checks.append({
            'name': 'middle_number_from_sum_of_squares',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kd.prove() certified that the positive solution of 3*n^2 + 8 = 12296 is n = 64.'
        })
    except Exception as e:
        checks.append({
            'name': 'middle_number_from_sum_of_squares',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove the middle-number theorem: {e}'
        })

    # Verified proof: compute the final value from the derived triple 62, 64, 66.
    a, b, c = Ints('a b c')
    try:
        thm_product = kd.prove(
            (62 * 64 * 66) / 8 == 32736
        )
        checks.append({
            'name': 'product_divided_by_8',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kd.prove() certified the arithmetic identity (62*64*66)/8 = 32736.'
        })
    except Exception as e:
        checks.append({
            'name': 'product_divided_by_8',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to certify the final arithmetic identity: {e}'
        })

    # Numerical sanity check with the concrete triple.
    try:
        val = (62**2 + 64**2 + 66**2)
        prod_div_8 = (62 * 64 * 66) // 8
        passed = (val == 12296) and (prod_div_8 == 32736)
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Sum of squares = {val}, product/8 = {prod_div_8}.'
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical evaluation failed: {e}'
        })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())