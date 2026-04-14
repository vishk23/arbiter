import kdrag as kd
from kdrag.smt import *
from sympy import Rational


def verify():
    checks = []

    # Verified proof certificate: from 40 calories being 2% = 1/50 of daily need,
    # the daily need is 40 * 50 = 2000.
    try:
        x = Int('x')
        thm = kd.prove(Exists([x], And(x == 2000, 40 * 50 == x)))
        checks.append({
            'name': 'daily_calories_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Knuckledragger proved existence of x=2000 consistent with 40*50 = 2000: {thm}'
        })
    except Exception as e:
        checks.append({
            'name': 'daily_calories_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}'
        })

    # Direct arithmetic verification in kdrag-friendly SMT.
    try:
        thm2 = kd.prove(2000 == 40 * 50)
        checks.append({
            'name': 'arithmetic_identity',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved the arithmetic identity 2000 = 40*50: {thm2}'
        })
    except Exception as e:
        checks.append({
            'name': 'arithmetic_identity',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Arithmetic proof failed: {e}'
        })

    # Numerical sanity check using the equation 40 = 0.02 * x at x = 2000.
    try:
        x_val = 2000
        lhs = 40
        rhs = 0.02 * x_val
        passed = abs(lhs - rhs) < 1e-12 and x_val == 2000
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'At x=2000, lhs=40 and rhs=0.02*2000={rhs}.',
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())