import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: from x+y=14 and xy=19, derive x^2+y^2=158.
    x, y = Reals('x y')
    thm = None
    try:
        thm = kd.prove(
            ForAll([x, y],
                   Implies(And((x + y) == 14, x * y == 19),
                           x * x + y * y == 158))
        )
        checks.append({
            'name': 'algebraic_derivation_x2_plus_y2',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'algebraic_derivation_x2_plus_y2',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check at a concrete solution: x=7+2*sqrt(3), y=7-2*sqrt(3)
    # This satisfies x+y=14 and xy=19, hence x^2+y^2=158.
    try:
        import math
        xv = 7 + 2 * math.sqrt(3)
        yv = 7 - 2 * math.sqrt(3)
        lhs1 = xv + yv
        lhs2 = xv * yv
        rhs = xv * xv + yv * yv
        passed = abs(lhs1 - 14.0) < 1e-9 and abs(lhs2 - 19.0) < 1e-9 and abs(rhs - 158.0) < 1e-9
        checks.append({
            'name': 'numerical_sanity_concrete_values',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'x+y={lhs1}, xy={lhs2}, x^2+y^2={rhs}'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_concrete_values',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved and all(c['passed'] for c in checks), 'checks': checks}


if __name__ == '__main__':
    print(verify())