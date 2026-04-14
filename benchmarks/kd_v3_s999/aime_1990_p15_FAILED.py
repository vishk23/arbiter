from sympy import Rational
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And, sat


def verify():
    checks = []
    proved_all = True

    # Verified algebraic proof using kdrag/Z3.
    # Variables represent the derived quantities S = x+y and P = xy.
    S = Real('S')
    P = Real('P')

    # From the given relations and the hint:
    # 7S = 16 + 3P and 16S = 42 + 7P.
    # Solving these linear equations yields S = -14 and P = -38.
    try:
        theorem_SP = kd.prove(
            ForAll([S, P], Implies(And(7*S == 16 + 3*P, 16*S == 42 + 7*P), And(S == -14, P == -38)))
        )
        checks.append({
            'name': 'solve_for_S_and_P',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(theorem_SP)
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'solve_for_S_and_P',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}'
        })

    # Final computation: 42S = T + 16P, where T = ax^5 + by^5.
    # With S = -14 and P = -38, T = 42*S - 16*P = 0.
    T = Real('T')
    try:
        theorem_T = kd.prove(
            ForAll([S, P, T], Implies(And(S == -14, P == -38, 42*S == T + 16*P), T == 0))
        )
        checks.append({
            'name': 'final_value_zero',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(theorem_T)
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'final_value_zero',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}'
        })

    # Numerical sanity check with the derived values.
    S_val = -14
    P_val = -38
    T_val = 42 * S_val - 16 * P_val
    num_passed = (T_val == 0)
    checks.append({
        'name': 'numerical_sanity_check',
        'passed': num_passed,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Computed T = 42*({S_val}) - 16*({P_val}) = {T_val}'
    })
    proved_all = proved_all and num_passed

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)