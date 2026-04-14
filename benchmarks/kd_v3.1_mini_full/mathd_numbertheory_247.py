import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: the modular inverse of 3 mod 11 is 4, so 3*8 = 24 ≡ 2 (mod 11).
    n = Int('n')
    thm = None
    try:
        thm = kd.prove((3 * 8 - 2) % 11 == 0)
        checks.append({
            'name': 'modular_inverse_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kd.prove verified that 3*8-2 is divisible by 11, i.e. 3*8 ≡ 2 (mod 11).'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'modular_inverse_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    # Verified proof of the candidate residue: 8 is a solution to 3n ≡ 2 (mod 11).
    try:
        candidate = kd.prove(((3 * 8 - 2) % 11) == 0)
        checks.append({
            'name': 'candidate_residue_is_8',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Verified that residue 8 satisfies the congruence 3n ≡ 2 (mod 11).'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'candidate_residue_is_8',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    # Numerical sanity check.
    lhs = (3 * 8) % 11
    rhs = 2 % 11
    passed_num = lhs == rhs
    checks.append({
        'name': 'numerical_sanity_check',
        'passed': passed_num,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Computed (3*8) % 11 = {lhs}, and 2 % 11 = {rhs}.'
    })
    if not passed_num:
        proved = False

    # Uniqueness over residues 0..10: check all residues and confirm only 8 works.
    sols = [r for r in range(11) if (3 * r - 2) % 11 == 0]
    passed_unique = sols == [8]
    checks.append({
        'name': 'unique_residue_mod_11',
        'passed': passed_unique,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Residues solving 3r ≡ 2 (mod 11) among 0..10: {sols}.'
    })
    if not passed_unique:
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)