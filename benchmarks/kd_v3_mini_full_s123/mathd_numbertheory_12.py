import kdrag as kd
from kdrag.smt import *


def _prove_count_multiples():
    n = Int('n')
    # Formal statement: integers between 15 and 85 divisible by 20 are exactly 4 in number.
    # We verify this by showing the only candidates are 20, 40, 60, 80.
    thm = kd.prove(
        ForAll([n],
            Implies(
                And(n >= 15, n <= 85, n % 20 == 0),
                Or(n == 20, n == 40, n == 60, n == 80)
            )
        )
    )
    return thm


def verify():
    checks = []
    proved = True

    # Check 1: Verified certificate that any multiple of 20 in [15,85] must be one of 20,40,60,80.
    try:
        proof1 = _prove_count_multiples()
        checks.append({
            'name': 'multiples_in_interval_are_among_four_candidates',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned proof: {proof1}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'multiples_in_interval_are_among_four_candidates',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}'
        })

    # Check 2: Numerical sanity check by brute force enumeration on concrete values.
    vals = [n for n in range(15, 86) if n % 20 == 0]
    passed2 = (len(vals) == 4 and vals == [20, 40, 60, 80])
    checks.append({
        'name': 'numerical_enumeration_sanity_check',
        'passed': passed2,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Enumerated values in [15,85] divisible by 20: {vals}; count={len(vals)}'
    })
    if not passed2:
        proved = False

    # Check 3: Symbolic arithmetic certificate for count formula.
    # Count of multiples of 20 in [15,85] is floor(85/20) - floor(14/20) = 4 - 0 = 4.
    # We verify the concrete arithmetic with exact integers.
    a = 85 // 20
    b = 14 // 20
    passed3 = (a - b == 4)
    checks.append({
        'name': 'closed_form_count_arithmetic',
        'passed': passed3,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'85//20={a}, 14//20={b}, difference={a-b}'
    })
    if not passed3:
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)