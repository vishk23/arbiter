import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: show the specific remainder is 34 by modular arithmetic.
    # Statement: 123456 ≡ 34 (mod 101), with 0 <= 34 < 101.
    try:
        n = Int('n')
        thm = kd.prove(And(0 <= 34, 34 < 101, (123456 - 34) % 101 == 0))
        checks.append({
            'name': 'congruence_123456_mod_101_is_34',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof object obtained: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'congruence_123456_mod_101_is_34',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove congruence with kdrag: {e}'
        })

    # Numerical sanity check: direct computation of the remainder.
    try:
        rem = 123456 % 101
        passed = (rem == 34)
        if not passed:
            proved = False
        checks.append({
            'name': 'numerical_remainder_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'123456 % 101 = {rem}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_remainder_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical computation failed: {e}'
        })

    # Additional verified proof: explicit quotient-remainder decomposition.
    try:
        q = Int('q')
        thm2 = kd.prove(Exists([q], 123456 == 101*q + 34))
        checks.append({
            'name': 'quotient_remainder_decomposition',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof object obtained: {thm2}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'quotient_remainder_decomposition',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove quotient-remainder decomposition with kdrag: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)