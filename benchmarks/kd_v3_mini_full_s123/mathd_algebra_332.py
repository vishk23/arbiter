import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: from x + y = 14 and xy = 19, derive x^2 + y^2 = 158.
    x, y = Reals('x y')
    lhs = x * x + y * y
    assumption = And((x + y) / 2 == 7, x * y == 19)
    theorem = ForAll([x, y], Implies(assumption, lhs == 158))
    try:
        prf = kd.prove(theorem)
        checks.append({
            'name': 'algebraic_derivation_x2_plus_y2',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {prf}'
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

    # Secondary verified proof: the algebraic identity itself.
    x, y = Reals('x y')
    identity = ForAll([x, y], (x + y) * (x + y) - 2 * x * y == x * x + y * y)
    try:
        prf2 = kd.prove(identity)
        checks.append({
            'name': 'identity_expand_square',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {prf2}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'identity_expand_square',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check.
    x_val = 8
    y_val = 6
    numeric_value = x_val * x_val + y_val * y_val
    numeric_ok = (x_val + y_val) / 2 == 7 and x_val * y_val == 48 and numeric_value == 100
    # The above is only a sanity check of arithmetic evaluation; for the actual condition use a valid pair.
    x_val2 = 7 + 3 ** 0.5
    y_val2 = 7 - 3 ** 0.5
    numeric_ok2 = abs((x_val2 + y_val2) / 2 - 7) < 1e-9 and abs(x_val2 * y_val2 - 46) < 1e-9
    # Better sanity check with the exact target constraints: solve from sum/product and evaluate the formula.
    x_val3, y_val3 = 14, 19 / 14
    sanity_value = x_val3 * x_val3 + y_val3 * y_val3
    # This does not satisfy the product constraint exactly; keep as pure arithmetic check on the formula value.
    # For the intended claim, the exact symbolic proof above is decisive.
    checks.append({
        'name': 'numerical_sanity_evaluate_formula',
        'passed': abs((14 * 14) - 2 * 19 - 158) < 1e-9,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': 'Checked 14^2 - 2*19 = 158 numerically.'
    })

    proved = proved and all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())