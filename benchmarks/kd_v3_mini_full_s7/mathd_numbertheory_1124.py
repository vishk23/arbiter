import kdrag as kd
from kdrag.smt import *


def _prove_digit_is_four():
    n = Int('n')
    # Formalize the exact claim over decimal digits.
    # If 374n is divisible by 18, then n is a digit and 3740+n is divisible by 18.
    thm = kd.prove(
        ForAll(
            [n],
            Implies(
                And(n >= 0, n <= 9, (3740 + n) % 18 == 0),
                n == 4,
            ),
        )
    )
    return thm


def verify():
    checks = []

    # Verified proof check via kdrag/Z3.
    try:
        proof = _prove_digit_is_four()
        checks.append(
            {
                'name': 'digit_uniqueness_from_divisibility_by_18',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kdrag proved: {proof}',
            }
        )
    except Exception as e:
        checks.append(
            {
                'name': 'digit_uniqueness_from_divisibility_by_18',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Proof attempt failed: {type(e).__name__}: {e}',
            }
        )

    # Numerical sanity check: concrete candidate.
    val = 3740 + 4
    num_ok = (val % 18 == 0)
    checks.append(
        {
            'name': 'numerical_sanity_check_for_n_equals_4',
            'passed': bool(num_ok),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'3744 % 18 == {val % 18}; thus 3744 is divisible by 18.',
        }
    )

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)