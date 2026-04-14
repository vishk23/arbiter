from sympy import Symbol, Integer, factorint
import kdrag as kd
from kdrag.smt import Ints, Int, ForAll, Implies, And


def verify():
    checks = []

    # Verified proof: derive 3x^2 y^2 = 588 from the given equation over integers.
    try:
        x, y = Ints('x y')
        thm = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(y*y + 3*x*x*y*y == 30*x*x + 517),
                    3*x*x*y*y == 588,
                ),
            )
        )
        checks.append(
            {
                'name': 'z3_proof_of_target_value',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': str(thm),
            }
        )
    except Exception as e:
        checks.append(
            {
                'name': 'z3_proof_of_target_value',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Z3 proof failed: {e}',
            }
        )

    # Symbolic sanity: factor the rearranged expression.
    try:
        x = Symbol('x', integer=True)
        y = Symbol('y', integer=True)
        lhs = y**2 + 3*x**2*y**2 - 30*x**2 - 517
        factored = (3*x**2 + 1)*(y**2 - 10) - 507
        passed = (lhs.expand() - factored.expand()) == 0
        checks.append(
            {
                'name': 'symbolic_factorization_check',
                'passed': passed,
                'backend': 'sympy',
                'proof_type': 'numerical',
                'details': 'Verified algebraic rearrangement: y^2 + 3x^2y^2 - 30x^2 - 517 = (3x^2+1)(y^2-10) - 507.',
            }
        )
    except Exception as e:
        checks.append(
            {
                'name': 'symbolic_factorization_check',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'numerical',
                'details': f'Symbolic check failed: {e}',
            }
        )

    # Numerical sanity check using the known solution x=2, y=7.
    try:
        xv = 2
        yv = 7
        lhs_val = yv * yv + 3 * xv * xv * yv * yv
        rhs_val = 30 * xv * xv + 517
        target_val = 3 * xv * xv * yv * yv
        passed = (lhs_val == rhs_val == 613) and (target_val == 588)
        checks.append(
            {
                'name': 'numerical_sanity_check',
                'passed': passed,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'x=2, y=7 gives lhs={lhs_val}, rhs={rhs_val}, and 3x^2y^2={target_val}.',
            }
        )
    except Exception as e:
        checks.append(
            {
                'name': 'numerical_sanity_check',
                'passed': False,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'Numerical check failed: {e}',
            }
        )

    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)