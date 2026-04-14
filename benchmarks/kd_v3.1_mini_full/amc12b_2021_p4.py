from sympy import Rational
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved_all = True

    # Verified proof: encode the weighted-average computation in kdrag.
    morning = Int('morning')
    afternoon = Int('afternoon')
    total = Int('total')
    weighted_sum = Int('weighted_sum')
    mean = Int('mean')

    # We prove the exact arithmetic statement that the weighted mean is 76.
    # Let morning = 3x and afternoon = 4x for some positive x; the common factor cancels.
    x = Int('x')
    theorem = ForAll([x], Implies(x > 0,
        ((3 * x * 84) + (4 * x * 70)) == 76 * (7 * x)
    ))

    try:
        proof = kd.prove(theorem)
        checks.append({
            'name': 'weighted_average_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned a proof object: {proof}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'weighted_average_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Symbolic arithmetic check using exact rational computation.
    try:
        answer = (84 * 3 + 70 * 4) / (3 + 4)
        passed = (answer == 76)
        checks.append({
            'name': 'exact_weighted_average',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Computed exact average = {answer}; expected 76.'
        })
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'exact_weighted_average',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Computation failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check at a concrete value x=5.
    try:
        x_val = 5
        morning_students = 3 * x_val
        afternoon_students = 4 * x_val
        numerical_mean = (morning_students * 84 + afternoon_students * 70) / (morning_students + afternoon_students)
        passed = (numerical_mean == 76)
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'For x=5, mean = {numerical_mean}.'
        })
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)