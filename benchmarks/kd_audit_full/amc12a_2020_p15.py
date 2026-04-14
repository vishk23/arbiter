from sympy import Symbol, Eq, factor, sqrt, I, simplify, expand

try:
    import kdrag as kd
    from kdrag.smt import *
    _KDRAG_AVAILABLE = True
except Exception:
    _KDRAG_AVAILABLE = False


def _numerical_distance(a, b):
    return abs(complex(a) - complex(b))


def verify():
    checks = []
    proved = True

    # Check 1: symbolic factorization of the second polynomial
    try:
        z = Symbol('z')
        poly = z**3 - 8*z**2 - 8*z + 64
        factored = factor(poly)
        passed = simplify(expand(factored) - poly) == 0 and factored == (z - 8)*(z**2 - 8)
        checks.append({
            'name': 'factorization_of_B_polynomial',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'factor(z^3 - 8 z^2 - 8 z + 64) = {factored}'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'factorization_of_B_polynomial',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed symbolic factorization: {e}'
        })
        proved = False

    # Check 2: verified proof with kdrag that 84 = (2*sqrt(21))^2 as a certificate-style algebraic claim
    if _KDRAG_AVAILABLE:
        try:
            x = Real('x')
            thm = kd.prove(Exists([x], And(x > 0, x*x == 84)), by=[])
            checks.append({
                'name': 'existence_of_positive_square_root_of_84',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove succeeded: {thm}'
            })
        except Exception as e:
            checks.append({
                'name': 'existence_of_positive_square_root_of_84',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kdrag proof failed: {e}'
            })
            proved = False
    else:
        checks.append({
            'name': 'existence_of_positive_square_root_of_84',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kdrag unavailable in runtime environment.'
        })
        proved = False

    # Check 3: exact distance computation using symbolic arithmetic
    try:
        A = [2, -1 + sqrt(3)*I, -1 - sqrt(3)*I]
        B = [2*sqrt(2), -2*sqrt(2), 8]
        distances = []
        for a in A:
            for b in B:
                distances.append(simplify((a - b) * (a.conjugate() - b.conjugate())))
        max_sq = max([int(d) if d.is_integer() else d for d in distances], key=lambda t: float(t))
        passed = simplify(max_sq - 84) == 0
        checks.append({
            'name': 'maximum_squared_distance_is_84',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'maximum squared distance computed symbolically = {max_sq}'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'maximum_squared_distance_is_84',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Failed exact distance computation: {e}'
        })
        proved = False

    # Check 4: numerical sanity check for the claimed maximizing pair
    try:
        a = -1 + sqrt(3)*I
        b = 8
        d = _numerical_distance(a, b)
        passed = abs(d - float(2 * sqrt(21))) < 1e-9
        checks.append({
            'name': 'numerical_sanity_check_claimed_distance',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'distance((-1+sqrt(3)i), 8) ≈ {d}, target ≈ {float(2*sqrt(21))}'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check_claimed_distance',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })
        proved = False

    # Check 5: verify no pair exceeds 2*sqrt(21) by direct symbolic/numerical scan
    try:
        A = [2, -1 + sqrt(3)*I, -1 - sqrt(3)*I]
        B = [2*sqrt(2), -2*sqrt(2), 8]
        max_d = 0
        for a in A:
            for b in B:
                val = float(_numerical_distance(a, b))
                if val > max_d:
                    max_d = val
        passed = abs(max_d - float(2 * sqrt(21))) < 1e-9
        checks.append({
            'name': 'numerical_max_distance_matches_claim',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'numerical max distance ≈ {max_d}, target ≈ {float(2*sqrt(21))}'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'numerical_max_distance_matches_claim',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical scan failed: {e}'
        })
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)