import kdrag as kd
from kdrag.smt import Int, And, ForAll, Implies


def verify():
    checks = []
    proved = True

    # Verified proof: 1058 is the multiplicative inverse of 160 modulo 1399.
    # We prove the stronger exact arithmetic claim 160*1058 = 1 + 1399*121,
    # which implies 160*1058 ≡ 1 (mod 1399).
    try:
        n = Int('n')
        thm = kd.prove(160 * 1058 == 1 + 1399 * 121)
        checks.append({
            'name': 'inverse_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove certified the exact identity 160*1058 = 1 + 1399*121: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'inverse_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to certify the modular inverse identity: {e}'
        })

    # Numerical sanity check at concrete values.
    lhs = 160 * 1058
    rhs = 1 + 1399 * 121
    num_passed = (lhs == rhs) and (lhs % 1399 == 1) and (1058 == 1058) and (0 <= 1058 < 1399)
    checks.append({
        'name': 'numerical_sanity',
        'passed': bool(num_passed),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Computed 160*1058={lhs}, and 160*1058 mod 1399 = {lhs % 1399}; also 0 <= 1058 < 1399.'
    })
    if not num_passed:
        proved = False

    # Independent arithmetic check that 1058 is the claimed inverse in the statement.
    try:
        claim = kd.prove(And(0 <= 1058, 1058 < 1399, (160 * 1058) % 1399 == 1))
        checks.append({
            'name': 'modular_inverse_claim',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove certified 0 <= 1058 < 1399 and (160*1058) % 1399 == 1: {claim}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'modular_inverse_claim',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to certify the modular inverse claim: {e}'
        })

    return {'proved': proved and all(c['passed'] for c in checks), 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)