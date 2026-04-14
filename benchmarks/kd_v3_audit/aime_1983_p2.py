import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved_all = True

    # Check 1: Verified proof that on p <= x <= 15, the absolute values simplify and f(x) = 30 - x.
    try:
        x = Real('x')
        p = Real('p')
        f = Abs(x - p) + Abs(x - 15) + Abs(x - p - 15)
        simplified = 30 - x

        thm1 = kd.prove(
            ForAll([x, p],
                   Implies(And(p > 0, p < 15, x >= p, x <= 15), f == simplified))
        )
        checks.append({
            'name': 'simplify_absolute_values_on_interval',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kd.prove certified that for 0 < p < 15 and p <= x <= 15, the expression equals 30 - x.'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'simplify_absolute_values_on_interval',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Check 2: Verified proof that 30 - x is minimized at x = 15 on the interval [p, 15].
    try:
        x = Real('x')
        p = Real('p')
        thm2 = kd.prove(
            ForAll([x, p],
                   Implies(And(p > 0, p < 15, x >= p, x <= 15), 30 - x >= 15))
        )
        checks.append({
            'name': 'minimum_value_lower_bound',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kd.prove certified the lower bound 30 - x >= 15 on the interval p <= x <= 15.'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'minimum_value_lower_bound',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Check 3: Numerical sanity check at a concrete point.
    try:
        p_val = 4
        x_val = 15
        f_val = abs(x_val - p_val) + abs(x_val - 15) + abs(x_val - p_val - 15)
        expected = 15
        passed = (f_val == expected)
        if not passed:
            proved_all = False
        checks.append({
            'name': 'numerical_sanity_at_endpoint',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'At p={p_val}, x={x_val}, f(x)={f_val}, expected {expected}.'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'numerical_sanity_at_endpoint',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)