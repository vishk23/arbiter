import kdrag as kd
from kdrag.smt import *


def _units_digit(n):
    return n % 10


def verify():
    checks = []
    proved = True

    # Verified proof: the sum of the units digits of multiples of 3 from 0 to 48 is 78.
    # Since the statement asks for multiples of 3 between 0 and 50, this is exactly the same list.
    try:
        k = Int('k')
        # Encode the concrete finite sum as a closed arithmetic term.
        total = Sum([_units_digit(3 * i) for i in range(17)])
        # The check is a concrete arithmetic identity: 0,3,6,...,48.
        proof = kd.prove(total == 78)
        checks.append({
            'name': 'sum_units_digits_multiples_of_3_0_to_50',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove certified the concrete equality total == 78; proof={proof}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sum_units_digits_multiples_of_3_0_to_50',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Could not certify the arithmetic identity with kdrag: {e}'
        })

    # Numerical sanity check.
    try:
        units = [(3 * k) % 10 for k in range(17)]
        answer = sum(units)
        passed = (answer == 78)
        if not passed:
            proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'units digits = {units}; sum = {answer}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical evaluation failed: {e}'
        })

    return {'proved': proved and all(c['passed'] for c in checks), 'checks': checks}


if __name__ == '__main__':
    print(verify())