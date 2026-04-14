import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved_all = True

    # Verified proof: from sqrt(19 + 3y) = 7, infer y = 10.
    # We encode the algebraic steps in Z3-friendly arithmetic.
    y = Real('y')
    premise = And(19 + 3 * y >= 0, 19 + 3 * y == 49)
    theorem = ForAll([y], Implies(And(19 + 3 * y >= 0, 7 * 7 == 19 + 3 * y), y == 10))
    # The theorem above is a direct algebraic encoding of the squaring step and simplification.
    # Z3 can prove the arithmetic consequence.
    try:
        proof = kd.prove(theorem)
        checks.append({
            'name': 'algebraic_deduction_y_equals_10',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {proof}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'algebraic_deduction_y_equals_10',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check: substitute y = 10 into the original equation.
    try:
        import math
        lhs = math.sqrt(19 + 3 * 10)
        rhs = 7
        passed = abs(lhs - rhs) < 1e-12
        if not passed:
            proved_all = False
        checks.append({
            'name': 'numerical_substitution_y_10',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'sqrt(19 + 3*10) = {lhs}, expected 7'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'numerical_substitution_y_10',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)