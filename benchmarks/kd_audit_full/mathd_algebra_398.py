from fractions import Fraction

import kdrag as kd
from kdrag.smt import Int, Ints, ForAll, Implies, And


def verify():
    checks = []

    # Verified proof: encode the unit conversion argument in Z3.
    ligs, lags, lugs = Ints('ligs lags lugs')
    theorem = ForAll([ligs, lags, lugs],
        Implies(
            And(7 * ligs == 4 * lags, 9 * lags == 20 * lugs, lugs == 80),
            ligs == 63
        )
    )

    try:
        proof = kd.prove(theorem)
        checks.append({
            'name': 'conversion_theorem_proved',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {proof}'
        })
    except Exception as e:
        checks.append({
            'name': 'conversion_theorem_proved',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check: compute the conversion ratio directly.
    # 7 ligs = 4 lags and 9 lags = 20 lugs => 1 lug = 9/20 lags = 9/20 * 4/7 ligs.
    # Thus 80 lugs = 80 * 9/20 * 4/7 = 63 ligs.
    try:
        ligs_per_lug = Fraction(9, 20) * Fraction(4, 7)
        value = 80 * ligs_per_lug
        passed = (value == 63)
        checks.append({
            'name': 'numerical_sanity_conversion',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Computed 80 lugs = {value} ligs using exact rational arithmetic.'
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_conversion',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical sanity check failed: {type(e).__name__}: {e}'
        })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)