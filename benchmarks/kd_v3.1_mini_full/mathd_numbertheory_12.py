import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Check 1: verified proof that exactly the multiples 20, 40, 60, 80 are in [15, 85]
    n = Int('n')
    thm = None
    try:
        thm = kd.prove(
            ForAll(
                [n],
                Implies(
                    And(n >= 15, n <= 85, n % 20 == 0),
                    Or(n == 20, n == 40, n == 60, n == 80),
                ),
            )
        )
        checks.append(
            {
                'name': 'multiples_of_20_in_interval_are_only_20_40_60_80',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove succeeded: {thm}',
            }
        )
    except Exception as e:
        checks.append(
            {
                'name': 'multiples_of_20_in_interval_are_only_20_40_60_80',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove failed: {type(e).__name__}: {e}',
            }
        )

    # Check 2: verified proof that each listed number is divisible by 20
    try:
        thm2 = kd.prove(
            And(20 % 20 == 0, 40 % 20 == 0, 60 % 20 == 0, 80 % 20 == 0)
        )
        checks.append(
            {
                'name': 'listed_numbers_are_divisible_by_20',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove succeeded: {thm2}',
            }
        )
    except Exception as e:
        checks.append(
            {
                'name': 'listed_numbers_are_divisible_by_20',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove failed: {type(e).__name__}: {e}',
            }
        )

    # Check 3: numerical sanity check by enumeration
    vals = [n for n in range(15, 86) if n % 20 == 0]
    count = len(vals)
    passed_num = (count == 4 and vals == [20, 40, 60, 80])
    checks.append(
        {
            'name': 'numerical_count_of_multiples_inclusive_interval',
            'passed': passed_num,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'enumerated values = {vals}, count = {count}',
        }
    )

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)