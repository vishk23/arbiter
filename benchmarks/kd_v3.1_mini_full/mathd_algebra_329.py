import kdrag as kd
from kdrag.smt import Ints, And, ForAll, Implies


def verify():
    checks = []
    proved = True

    # Verified proof: solve the linear system in Z3 using kdrag.
    x, y = Ints('x y')
    check_name = 'intersection_sum_is_4'
    try:
        thm = kd.prove(
            ForAll([x, y],
                   Implies(And(x == 3 * y, 2 * x + 5 * y == 11), x + y == 4))
        )
        passed = True
        details = f'Proved with kdrag certificate: {thm}'
    except Exception as e:
        passed = False
        proved = False
        details = f'kdrag proof failed: {type(e).__name__}: {e}'
    checks.append({
        'name': check_name,
        'passed': passed,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': details,
    })

    # Numerical sanity check at the concrete solution x=3, y=1.
    check_name = 'numerical_sanity_at_solution'
    try:
        x0, y0 = 3, 1
        passed = (x0 == 3 * y0) and (2 * x0 + 5 * y0 == 11) and (x0 + y0 == 4)
        details = f'Checked x=3, y=1: equations and sum evaluate to {x0 + y0}.'
    except Exception as e:
        passed = False
        proved = False
        details = f'Numerical check failed: {type(e).__name__}: {e}'
    checks.append({
        'name': check_name,
        'passed': passed,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': details,
    })

    return {'proved': proved and all(c['passed'] for c in checks), 'checks': checks}


if __name__ == '__main__':
    print(verify())