import kdrag as kd
from kdrag.smt import Ints, ForAll, Implies, And
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof: formal derivation from the linear system.
    N, x = Ints('N x')
    theorem = ForAll([N, x], Implies(And(N + x == 97, N + 5 * x == 265), N + 2 * x == 139))
    try:
        proof = kd.prove(theorem)
        checks.append({
            'name': 'linear_system_to_two_hour_charge',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(proof),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'linear_system_to_two_hour_charge',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}',
        })

    # Numerical sanity check at the concrete solution N=55, x=42.
    try:
        n_val = 55
        x_val = 42
        calc_1 = n_val + x_val
        calc_5 = n_val + 5 * x_val
        calc_2 = n_val + 2 * x_val
        passed = (calc_1 == 97 and calc_5 == 265 and calc_2 == 139)
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'N={n_val}, x={x_val}; 1-hour={calc_1}, 5-hour={calc_5}, 2-hour={calc_2}',
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}',
        })

    return {'proved': proved and all(c['passed'] for c in checks), 'checks': checks}


if __name__ == '__main__':
    print(verify())