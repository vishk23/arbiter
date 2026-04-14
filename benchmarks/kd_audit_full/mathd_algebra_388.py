from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, Ints, ForAll, Implies, And


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: derive x = 14 from the transformed linear system.
    x, w = Ints('x w')
    theorem = ForAll([x, w], Implies(And(3 * x + 4 * w == 10, -2 * x - 3 * w == -4), x == 14))
    try:
        proof = kd.prove(theorem)
        checks.append({
            'name': 'linear_elimination_proves_x_equals_14',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded with proof: {proof}',
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'linear_elimination_proves_x_equals_14',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {type(e).__name__}: {e}',
        })

    # Sanity check on the claimed value x = 14.
    try:
        x_val = 14
        w_val = -8  # From 3x + 4w = 10 => 42 + 4w = 10 => w = -8
        eq1 = (3 * x_val + 4 * w_val == 10)
        eq2 = (-2 * x_val - 3 * w_val == -4)
        passed = bool(eq1 and eq2)
        checks.append({
            'name': 'numerical_sanity_check_at_x_14',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'With x=14 and w=-8, equation 1 is {eq1}, equation 2 is {eq2}.',
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check_at_x_14',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}',
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)