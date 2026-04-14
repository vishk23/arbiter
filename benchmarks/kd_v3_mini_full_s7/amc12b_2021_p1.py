from sympy import pi
import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify():
    checks = []

    # The exact answer is the count of integers x with -3*pi < x < 3*pi.
    # Since 9 < 3*pi < 10, the integers are -9,-8,...,8,9.
    # We use kdrag to certify the integer interval implication with the lower/upper bounds.
    x = Int('x')
    try:
        # If -9 <= x <= 9 and x is integer, then |x| < 3*pi.
        # This follows from 9 < 3*pi.
        thm = kd.prove(ForAll([x], Implies(And(x >= -9, x <= 9), abs(x) < 3*pi)))
        checks.append({
            'name': 'prove_integers_from_minus9_to_9_satisfy_bound',
            'passed': True,
            'backend': 'kdrag',
            'details': str(thm),
        })
    except Exception as e:
        checks.append({
            'name': 'prove_integers_from_minus9_to_9_satisfy_bound',
            'passed': False,
            'backend': 'kdrag',
            'details': f'{type(e).__name__}: {e}',
        })

    # Direct numeric boundary check for the problem statement.
    boundary_ok = (9 < 3*pi) and (3*pi < 10)
    checks.append({
        'name': 'verify_9_less_than_3pi_less_than_10',
        'passed': bool(boundary_ok),
        'backend': 'sympy',
        'details': 'Confirms the open interval (-3*pi, 3*pi) contains exactly the integers -9 through 9.',
    })

    # Count the integers explicitly: -9,-8,...,8,9.
    count = len(list(range(-9, 10)))
    checks.append({
        'name': 'count_integers_minus9_to_9',
        'passed': count == 19,
        'backend': 'python',
        'details': f'Counted {count} integers.',
    })

    return checks