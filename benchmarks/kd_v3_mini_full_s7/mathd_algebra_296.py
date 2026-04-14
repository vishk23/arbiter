import kdrag as kd
from kdrag.smt import Int


def verify():
    checks = []

    # Verified proof: the area change is exactly -3600, so the amount of decrease is 3600.
    try:
        n = Int('n')
        thm = kd.prove((3491 - 60) * (3491 + 60) - 3491 * 3491 == -3600)
        checks.append({
            'name': 'area_change_exactly_minus_3600',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm),
        })
    except Exception as e:
        checks.append({
            'name': 'area_change_exactly_minus_3600',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}',
        })

    # Numerical sanity check
    try:
        original = 3491 * 3491
        new_area = (3491 - 60) * (3491 + 60)
        change = new_area - original
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': change == -3600,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'original={original}, new_area={new_area}, change={change}',
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'numerical check failed: {e}',
        })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)