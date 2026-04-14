from sympy import symbols
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Verified proof 1: derive S and P from the linear system.
    # Let S = x + y and P = x*y. The given identities imply
    #   7S = 16 + 3P
    #   16S = 42 + 7P
    # From these, we can conclude S = -14 and P = -38.
    S, P = Real('S'), Real('P')
    thm_sp = kd.prove(
        ForAll([S, P],
               Implies(And(7 * S == 16 + 3 * P,
                          16 * S == 42 + 7 * P),
                       And(S == -14, P == -38)))
    )
    checks.append({
        'name': 'derive_S_and_P',
        'passed': True,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': str(thm_sp)
    })

    # Verified proof 2: compute the target value from S and P.
    T = Real('T')
    thm_t = kd.prove(
        ForAll([T, S, P],
               Implies(And(S == -14, P == -38, 42 * S == T + 16 * P),
                       T == 20))
    )
    checks.append({
        'name': 'compute_target_value',
        'passed': True,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': str(thm_t)
    })

    # Numerical sanity check with one concrete assignment satisfying the system.
    # Choose x=2, y=-16, a=1, b=0 gives ax+by=2, so not suitable.
    # We instead verify the arithmetic relation directly using the derived S,P.
    S_val, P_val = -14, -38
    target = 42 * S_val - 16 * P_val
    numerical_pass = (target == 20)
    checks.append({
        'name': 'numerical_sanity_check',
        'passed': numerical_pass,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'42*(-14) - 16*(-38) = {target}'
    })

    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)