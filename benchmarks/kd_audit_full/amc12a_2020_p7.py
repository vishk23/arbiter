from sympy import Integer, Rational

try:
    import kdrag as kd
    from kdrag.smt import *
    _KDRAG_AVAILABLE = True
except Exception:
    _KDRAG_AVAILABLE = False


def _numerical_tower_surface_area():
    # Concrete evaluation for the AMC tower with side lengths 1,2,3,4,5,6,7.
    sides = [1, 2, 3, 4, 5, 6, 7]
    side_area = 4 * sum(n * n for n in sides)
    top_area = 7 * 7
    bottom_area = 7 * 7
    total = side_area + top_area + bottom_area
    return side_area, top_area, bottom_area, total


def verify():
    checks = []
    proved = True

    # Verified proof: the side area sum is exactly 4*sum_{n=1}^7 n^2 = 560.
    if _KDRAG_AVAILABLE:
        n = Int('n')
        try:
            side_sum = kd.prove(Exists([n], And(n == 560, n == 4 * (1*1 + 2*2 + 3*3 + 4*4 + 5*5 + 6*6 + 7*7))))
            # The above is a certificate of the arithmetic identity encoded as an existential witness.
            checks.append({
                'name': 'side_area_arithmetic_certificate',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kdrag produced proof object: {side_sum}'
            })
        except Exception as e:
            proved = False
            checks.append({
                'name': 'side_area_arithmetic_certificate',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kdrag proof failed: {e}'
            })
    else:
        proved = False
        checks.append({
            'name': 'side_area_arithmetic_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kdrag unavailable in this environment.'
        })

    # Verified symbolic algebra: the difference of consecutive square areas telescopes to 49.
    # We use exact integer arithmetic in SymPy for a symbolic check of the computed quantity.
    try:
        top_area = sum((Integer(n) ** 2 - Integer(n - 1) ** 2) for n in range(2, 8)) + Integer(1)
        bottom_area = Integer(7) ** 2
        assert top_area == 49
        assert bottom_area == 49
        checks.append({
            'name': 'top_bottom_area_exact',
            'passed': True,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'Exact symbolic computation shows top area = 49 and bottom area = 49.'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'top_bottom_area_exact',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Symbolic verification failed: {e}'
        })

    # Numerical sanity check at the concrete values from the problem.
    try:
        side_area, top_area, bottom_area, total = _numerical_tower_surface_area()
        ok = (side_area == 560 and top_area == 49 and bottom_area == 49 and total == 658)
        checks.append({
            'name': 'numerical_surface_area_total',
            'passed': ok,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'side={side_area}, top={top_area}, bottom={bottom_area}, total={total}'
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_surface_area_total',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)