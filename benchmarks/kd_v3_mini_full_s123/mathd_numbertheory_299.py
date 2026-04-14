import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved_all = True

    # Certified proof of the exact product value.
    try:
        prod = 1 * 3 * 5 * 7 * 9 * 11 * 13
        proof_prod = kd.prove(prod == 135135)
        checks.append({
            'name': 'exact_product_value',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Certified by kdrag proof object: {proof_prod}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'exact_product_value',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Certified proof that the ones digit is 5.
    try:
        prod = 1 * 3 * 5 * 7 * 9 * 11 * 13
        proof_mod = kd.prove(prod % 10 == 5)
        checks.append({
            'name': 'ones_digit_is_5',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Certified by kdrag proof object: {proof_mod}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'ones_digit_is_5',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check.
    try:
        prod_num = 1
        for a in [1, 3, 5, 7, 9, 11, 13]:
            prod_num *= a
        passed = (prod_num == 135135) and (prod_num % 10 == 5)
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Computed product={prod_num}; product % 10 = {prod_num % 10}.'
        })
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)