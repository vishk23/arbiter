import kdrag as kd
from kdrag.smt import *


def _ones_digit_of_product_proof():
    # Formalized arithmetic theorem: the product 1*3*5*7*9*11*13 ends in 5.
    # We prove the exact modular equation in Z3.
    prod_val = 1 * 3 * 5 * 7 * 9 * 11 * 13
    return kd.prove(prod_val % 10 == 5)


def _mod_step_certification():
    # A small verified fact used as a sanity certificate:
    # multiplying by 5 forces the ones digit to be 5.
    n = Int('n')
    thm = kd.prove(ForAll([n], Implies(n % 2 == 1, (n * 5) % 10 == 5)))
    return thm


def verify():
    checks = []
    proved_all = True

    # Verified proof check: the exact product modulo 10 is 5.
    try:
        p = _ones_digit_of_product_proof()
        checks.append({
            'name': 'product_mod_10_is_5',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove certificate obtained: {p}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'product_mod_10_is_5',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Additional verified proof: odd times 5 ends in 5.
    try:
        p2 = _mod_step_certification()
        checks.append({
            'name': 'odd_times_five_ends_in_five',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove certificate obtained: {p2}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'odd_times_five_ends_in_five',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check.
    prod = 1 * 3 * 5 * 7 * 9 * 11 * 13
    numeric_passed = (prod % 10 == 5)
    checks.append({
        'name': 'numerical_sanity_check',
        'passed': numeric_passed,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Computed product={prod}, product % 10 = {prod % 10}'
    })
    if not numeric_passed:
        proved_all = False

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)