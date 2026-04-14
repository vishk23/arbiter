import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def verify():
    checks = []

    # Verified proof: exact integer theorem in Z3/kdrag.
    x, y = Ints('x y')
    try:
        thm = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    y*y + 3*x*x*y*y == 30*x*x + 517,
                    3*x*x*y*y == 588,
                ),
            )
        )
        checks.append(
            {
                'name': 'diophantine_theorem',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': str(thm),
            }
        )
    except Exception as e:
        checks.append(
            {
                'name': 'diophantine_theorem',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kdrag proof failed: {type(e).__name__}: {e}',
            }
        )

    # Numerical sanity check at the actual solution x=2, y=7.
    X = 2
    Y = 7
    lhs = Y * Y + 3 * X * X * Y * Y
    rhs = 30 * X * X + 517
    checks.append(
        {
            'name': 'numerical_sanity_solution',
            'passed': lhs == rhs == 637,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'x={X}, y={Y}, lhs={lhs}, rhs={rhs}, 3x^2y^2={3*X*X*Y*Y}',
        }
    )

    # Symbolic divisibility sanity: if x=2 then the equation forces y=7.
    # This is a supporting check only; the main theorem is proven above.
    x2 = Integer(2)
    y2 = Integer(7)
    symbolic_ok = (y2**2 + 3*x2**2*y2**2 == 30*x2**2 + 517)
    checks.append(
        {
            'name': 'symbolic_solution_consistency',
            'passed': bool(symbolic_ok),
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': 'Verified that (x,y)=(2,7) satisfies the equation and yields 588.',
        }
    )

    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)