from fractions import Fraction

import kdrag as kd
from kdrag.smt import Real, Reals, ForAll, Implies, And


def verify():
    checks = []

    # Verified proof: if x,y,z satisfy the three equations, then x+y+z=12.
    x, y, z = Reals('x y z')
    thm = ForAll(
        [x, y, z],
        Implies(
            And(3 * x + y == 17, 5 * y + z == 14, 3 * x + 5 * z == 41),
            x + y + z == 12,
        ),
    )
    try:
        proof = kd.prove(thm)
        checks.append({
            'name': 'algebraic_sum_is_12',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(proof),
        })
    except Exception as e:
        checks.append({
            'name': 'algebraic_sum_is_12',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}',
        })

    # Numerical sanity check using the unique solution from the linear system.
    # Solve manually from the equations:
    #   x = 47/14, y = 11/2, z = 9/2
    xv = Fraction(47, 14)
    yv = Fraction(11, 2)
    zv = Fraction(9, 2)
    lhs1 = 3 * xv + yv
    lhs2 = 5 * yv + zv
    lhs3 = 3 * xv + 5 * zv
    sumv = xv + yv + zv
    numerical_passed = (lhs1 == 17 and lhs2 == 14 and lhs3 == 41 and sumv == 12)
    checks.append({
        'name': 'numerical_sanity_check',
        'passed': numerical_passed,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': (
            f'x={xv}, y={yv}, z={zv}; '
            f'3x+y={lhs1}, 5y+z={lhs2}, 3x+5z={lhs3}, x+y+z={sumv}'
        ),
    })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)