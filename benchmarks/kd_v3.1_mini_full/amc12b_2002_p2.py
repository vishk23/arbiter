import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []

    # Verified proof via kdrag: the expression simplifies to 3*x - 1 for all x,
    # hence at x = 4 it equals 11.
    x = Real('x')
    expr = (3 * x - 2) * (4 * x + 1) - (3 * x - 2) * (4 * x) + 1
    try:
        thm = kd.prove(ForAll([x], expr == 3 * x - 1))
        checks.append({
            'name': 'algebraic_simplification_identity',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned proof: {thm}'
        })
    except Exception as e:
        checks.append({
            'name': 'algebraic_simplification_identity',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove symbolic identity with kdrag: {e}'
        })

    # Concrete theorem at x = 4
    try:
        val = 11
        thm2 = kd.prove(substitute(expr, [(x, RealVal(4))]) == RealVal(val))
        checks.append({
            'name': 'value_at_x_equals_4',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned proof: {thm2}'
        })
    except Exception as e:
        checks.append({
            'name': 'value_at_x_equals_4',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove value at x=4 with kdrag: {e}'
        })

    # Numerical sanity check
    x_num = 4
    numeric_value = (3 * x_num - 2) * (4 * x_num + 1) - (3 * x_num - 2) * (4 * x_num) + 1
    checks.append({
        'name': 'numerical_evaluation_at_4',
        'passed': numeric_value == 11,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Computed value at x=4 is {numeric_value}.'
    })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())