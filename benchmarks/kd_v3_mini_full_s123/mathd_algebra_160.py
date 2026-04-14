from sympy import symbols, Eq, solve, Integer
import kdrag as kd
from kdrag.smt import Ints, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Verified symbolic proof via kdrag: encode the linear system and the target claim.
    try:
        N, x = Ints('N x')
        theorem = ForAll([N, x], Implies(And(N + x == 97, N + 5*x == 265), N + 2*x == 139))
        pf = kd.prove(theorem)
        checks.append({
            'name': 'linear_system_implies_two_hour_charge',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(pf)
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'linear_system_implies_two_hour_charge',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    # SymPy computation of the exact solution and the target value.
    try:
        N, x = symbols('N x')
        sol = solve([Eq(N + x, 97), Eq(N + 5*x, 265)], [N, x], dict=True)
        target = None
        if sol:
            target = sol[0][N] + 2 * sol[0][x]
        passed = bool(sol) and target == Integer(139)
        checks.append({
            'name': 'sympy_solve_and_evaluate',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'solution={sol}, two_hour_charge={target}'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_solve_and_evaluate',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy check failed: {e}'
        })

    # Numerical sanity check at the concrete derived values N=55, x=42.
    try:
        N_val = 55
        x_val = 42
        one_hour = N_val + x_val
        five_hour = N_val + 5 * x_val
        two_hour = N_val + 2 * x_val
        passed = (one_hour == 97) and (five_hour == 265) and (two_hour == 139)
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'N=55, x=42 -> 1h={one_hour}, 5h={five_hour}, 2h={two_hour}'
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
            'details': f'Numerical check failed: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())