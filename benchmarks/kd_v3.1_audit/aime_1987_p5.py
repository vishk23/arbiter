import kdrag as kd
from kdrag.smt import *
from math import isqrt
import sympy as sp


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: Verified kdrag proof that any integer solution forces 3*x^2*y^2 = 588.
    x, y = Ints('x y')
    try:
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
                'name': 'diophantine_implication',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove succeeded: {thm}',
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'diophantine_implication',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kdrag proof failed: {type(e).__name__}: {e}',
            }
        )

    # Check 2: SymPy symbolic exact verification of the intended solution.
    # Using the unique integer solution (x,y) = (2,7), we verify the equation and value exactly.
    try:
        X = sp.Integer(2)
        Y = sp.Integer(7)
        lhs = Y**2 + 3 * X**2 * Y**2
        rhs = 30 * X**2 + 517
        value = 3 * X**2 * Y**2
        passed = sp.simplify(lhs - rhs) == 0 and sp.simplify(value - 588) == 0
        if not passed:
            proved = False
        checks.append(
            {
                'name': 'symbolic_solution_verification',
                'passed': bool(passed),
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Checked exact candidate (x,y)=(2,7): lhs={lhs}, rhs={rhs}, 3x^2y^2={value}.',
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'symbolic_solution_verification',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'SymPy verification failed: {type(e).__name__}: {e}',
            }
        )

    # Check 3: Numerical sanity check on the recovered solution.
    try:
        X = 2
        Y = 7
        lhs_n = Y * Y + 3 * X * X * Y * Y
        rhs_n = 30 * X * X + 517
        val_n = 3 * X * X * Y * Y
        passed = (lhs_n == rhs_n) and (val_n == 588)
        if not passed:
            proved = False
        checks.append(
            {
                'name': 'numerical_sanity_check',
                'passed': bool(passed),
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'For x=2, y=7: lhs={lhs_n}, rhs={rhs_n}, 3x^2y^2={val_n}.',
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'numerical_sanity_check',
                'passed': False,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'Numerical check failed: {type(e).__name__}: {e}',
            }
        )

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())