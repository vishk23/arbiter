import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved_all = True

    # Check 1: Verified proof in kdrag that 575 increased by 4% is 598.
    try:
        x = Real('x')
        thm = kd.prove(ForAll([x], Implies(x == 575, x + x / 25 == 598)))
        checks.append({
            'name': '4_percent_growth_equation',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm)
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': '4_percent_growth_equation',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to verify 575 + 4% of 575 = 598: {e}'
        })

    # Check 2: Verified proof in kdrag that the enrollment equation has unique solution 575.
    try:
        x = Real('x')
        thm = kd.prove(ForAll([x], Implies(1.04 * x == 598, x == 575)))
        checks.append({
            'name': 'solve_enrollment_equation',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm)
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'solve_enrollment_equation',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove 1.04*x = 598 implies x = 575: {e}'
        })

    # Check 3: Numerical sanity check.
    try:
        val = 575 * 1.04
        passed = abs(val - 598) < 1e-9
        if not passed:
            proved_all = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'575 * 1.04 = {val}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    print(verify())