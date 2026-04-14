import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Check 1: Verified certificate proof of the algebraic deduction that the son's age is 6.
    try:
        x = Real('x')
        y = Real('y')
        thm = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(y == 5 * x, (x - 3) + (y - 3) == 30),
                    x == 6,
                ),
            )
        )
        checks.append(
            {
                'name': 'deduce_sons_age_is_6',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': str(thm),
            }
        )
    except Exception as e:
        checks.append(
            {
                'name': 'deduce_sons_age_is_6',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Proof failed: {e}',
            }
        )

    # Check 2: Numerical sanity check at the concrete solution x=6, y=30.
    x_val = 6
    y_val = 30
    passed_num = (y_val == 5 * x_val) and ((x_val - 3) + (y_val - 3) == 30)
    checks.append(
        {
            'name': 'numerical_sanity_at_solution',
            'passed': bool(passed_num),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'x={x_val}, y={y_val}; verifies y=5x and three-years-ago sum is 30',
        }
    )

    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)