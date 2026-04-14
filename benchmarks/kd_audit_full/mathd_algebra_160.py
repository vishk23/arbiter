from typing import Dict, Any, List

import kdrag as kd
from kdrag.smt import Ints, ForAll, Implies


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved_all = True

    # Verified proof: derive the two-hour charge from the system of equations.
    # Let N be the fixed coming-out charge and x be the hourly rate.
    N, x = Ints('N x')
    theorem = ForAll(
        [N, x],
        Implies(
            (N + x == 97) & (N + 5 * x == 265),
            N + 2 * x == 139,
        ),
    )
    try:
        prf = kd.prove(theorem)
        checks.append({
            'name': 'derive_two_hour_charge',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {prf}',
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'derive_two_hour_charge',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}',
        })

    # Numerical sanity check using the inferred values N=55, x=42.
    N_val, x_val = 55, 42
    two_hour_charge = N_val + 2 * x_val
    passed_num = (N_val + x_val == 97) and (N_val + 5 * x_val == 265) and (two_hour_charge == 139)
    checks.append({
        'name': 'numerical_sanity_check',
        'passed': passed_num,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Using N=55, x=42: one-hour={N_val + x_val}, five-hour={N_val + 5 * x_val}, two-hour={two_hour_charge}.',
    })
    proved_all = proved_all and passed_num

    # Direct algebraic consistency check: the system implies x=42 and N=55.
    # This is also Z3-encodable and serves as an extra verified lemma.
    theorem2 = ForAll(
        [N, x],
        Implies(
            (N + x == 97) & (N + 5 * x == 265),
            (x == 42) & (N == 55),
        ),
    )
    try:
        prf2 = kd.prove(theorem2)
        checks.append({
            'name': 'solve_for_parameters',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {prf2}',
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'solve_for_parameters',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}',
        })

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)