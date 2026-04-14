from kdrag.smt import *
import kdrag as kd


def verify():
    checks = []

    # Verified proof via Z3/Knuckledragger: 1529 = 254*6 + 5 and hence 1529 mod 6 = 5.
    try:
        q = Int('q')
        thm = kd.prove(Exists([q], 1529 == 6 * q + 5))
        checks.append({
            'name': 'existence_of_quotient_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {thm}'
        })
    except Exception as e:
        checks.append({
            'name': 'existence_of_quotient_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {e}'
        })

    # Direct modular arithmetic certificate: 1529 = 6*254 + 5.
    try:
        q = Int('q')
        thm2 = kd.prove(1529 == 6 * 254 + 5)
        checks.append({
            'name': 'explicit_decomposition_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {thm2}'
        })
    except Exception as e:
        checks.append({
            'name': 'explicit_decomposition_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {e}'
        })

    # Numerical sanity check.
    remainder = 1529 % 6
    num_ok = (remainder == 5)
    checks.append({
        'name': 'numerical_mod_check',
        'passed': num_ok,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'1529 % 6 = {remainder}, expected 5'
    })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())