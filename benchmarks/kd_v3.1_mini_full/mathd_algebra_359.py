import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified proof: encode the arithmetic-sequence condition and prove y = 9.
    y = Real('y')
    seq_condition = (12 - (y + 6)) == (y - 12)
    theorem = ForAll([y], Implies(seq_condition, y == 9))
    try:
        proof = kd.prove(theorem)
        checks.append({
            'name': 'arithmetic_sequence_implies_y_equals_9',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned a Proof object: {proof}'
        })
    except Exception as e:
        checks.append({
            'name': 'arithmetic_sequence_implies_y_equals_9',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check at the claimed solution y = 9.
    y_val = 9
    left_diff = 12 - (y_val + 6)
    right_diff = y_val - 12
    checks.append({
        'name': 'numerical_sanity_check_at_y_9',
        'passed': (left_diff == right_diff == -3),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'at y=9, differences are left={left_diff}, right={right_diff}'
    })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())