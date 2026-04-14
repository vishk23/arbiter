import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify():
    checks = []

    # Verified proof: the expression has units digit 2, i.e. it is congruent to 2 mod 10.
    try:
        n = Int('n')
        expr = 29 * 79 + 31 * 81
        # The concrete arithmetic is Z3-encodable; prove the exact modular fact.
        proof = kd.prove(expr % 10 == 2)
        checks.append({
            'name': 'units_digit_congruence',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove certified that ({expr}) % 10 == 2; proof={proof}',
        })
    except Exception as e:
        checks.append({
            'name': 'units_digit_congruence',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to certify congruence modulo 10: {e}',
        })

    # Numerical sanity check.
    try:
        val = 29 * 79 + 31 * 81
        checks.append({
            'name': 'numerical_evaluation',
            'passed': (val == 3368 and val % 10 == 8) is False and (val % 10 == 2),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Computed value {val}; units digit is {val % 10}.',
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_evaluation',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical evaluation failed: {e}',
        })

    # Direct digit computation from the hint, as an additional symbolic sanity check.
    try:
        units = ((29 * 79 + 31 * 81) % 10)
        checks.append({
            'name': 'direct_mod_10_computation',
            'passed': units == 2,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'((29*79 + 31*81) % 10) = {units}.',
        })
    except Exception as e:
        checks.append({
            'name': 'direct_mod_10_computation',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Direct modular computation failed: {e}',
        })

    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)