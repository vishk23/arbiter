import kdrag as kd
from kdrag.smt import *


def _prove_main_theorem():
    n = Int('n')
    q = Int('q')
    # If n leaves remainder 3 upon division by 5, then n = 5q + 3 for some integer q.
    # We prove that 2n leaves remainder 1 upon division by 5.
    thm = kd.prove(
        ForAll([n], Implies(Exists([q], n == 5*q + 3), Exists([q], 2*n == 5*q + 1)))
    )
    return thm


def verify():
    checks = []
    proved = True

    # Verified proof certificate via kdrag/Z3.
    try:
        proof1 = _prove_main_theorem()
        checks.append({
            'name': 'main_theorem_remainder_3_to_1',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(proof1),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'main_theorem_remainder_3_to_1',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}',
        })

    # Numerical sanity check: choose a concrete number 8 = 5*1 + 3.
    n_val = 8
    rem = (2 * n_val) % 5
    passed_num = (rem == 1)
    checks.append({
        'name': 'numerical_sanity_example_8',
        'passed': passed_num,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'For n=8, 2n mod 5 = {rem}.',
    })
    if not passed_num:
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)