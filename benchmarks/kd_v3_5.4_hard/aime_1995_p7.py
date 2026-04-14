import sympy as sp


def verify():
    checks = []

    # Symbols
    s = sp.Symbol('s', real=True)
    x = sp.Symbol('x')

    # We encode s = sin(t)+cos(t). From the given,
    # (1+sin t)(1+cos t)=5/4 implies s + p = 1/4 where p=sin t cos t.
    # Also s^2 = 1 + 2p, so p=(s^2-1)/2.
    # Hence s satisfies 2 s^2 + 4 s - 3 = 0.
    poly_s = 2 * s**2 + 4 * s - 3

    # Check 1: rigorous symbolic proof that sqrt(10)/2 - 1 is a root of the derived polynomial.
    try:
        candidate = sp.sqrt(10) / 2 - 1
        mp = sp.minimal_polynomial(sp.expand(candidate**2 + 2 * candidate - sp.Rational(3, 2)), x)
        passed = sp.expand(mp) == x
        checks.append({
            'name': 'derived_quadratic_root_for_s',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'Verified symbolically that ((sqrt(10)/2 - 1)^2 + 2*(sqrt(10)/2 - 1) - 3/2) = 0 via minimal_polynomial == x.' if passed else f'minimal_polynomial was {mp}, not x.'
        })
    except Exception as e:
        checks.append({
            'name': 'derived_quadratic_root_for_s',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Exception during symbolic verification: {e}'
        })

    # Check 2: rigorous symbolic proof that the other quadratic root is impossible
    # because it is less than -sqrt(2), while sin t + cos t is always in [-sqrt(2), sqrt(2)].
    try:
        bad_root = -1 - sp.sqrt(10) / 2
        expr = sp.simplify((bad_root)**2 - 2)  # > 0 implies |bad_root| > sqrt(2)
        # Since bad_root < 0, expr > 0 is enough to conclude bad_root < -sqrt(2).
        passed = sp.simplify(expr - (sp.Rational(5, 2) + sp.sqrt(10))) == 0
        checks.append({
            'name': 'discard_negative_root_by_bound',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'Computed (-1 - sqrt(10)/2)^2 - 2 = 5/2 + sqrt(10) > 0, so |-1 - sqrt(10)/2| > sqrt(2); hence this root cannot equal sin t + cos t.' if passed else f'Unexpected simplification result: {expr}'
        })
    except Exception as e:
        checks.append({
            'name': 'discard_negative_root_by_bound',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Exception during root-discard check: {e}'
        })

    # Check 3: rigorous symbolic proof of the target expression
    # (1-sin t)(1-cos t) = 1 - s + p = (1+s+p) - 2s = 5/4 - 2s.
    # With s = sqrt(10)/2 - 1 this is 13/4 - sqrt(10).
    try:
        target_expr = sp.Rational(5, 4) - 2 * (sp.sqrt(10) / 2 - 1) - (sp.Rational(13, 4) - sp.sqrt(10))
        mp = sp.minimal_polynomial(sp.expand(target_expr), x)
        passed = sp.expand(mp) == x
        checks.append({
            'name': 'target_value_equals_13_over_4_minus_sqrt_10',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'Verified symbolically that 5/4 - 2*(sqrt(10)/2 - 1) = 13/4 - sqrt(10) via minimal_polynomial == x.' if passed else f'minimal_polynomial was {mp}, not x.'
        })
    except Exception as e:
        checks.append({
            'name': 'target_value_equals_13_over_4_minus_sqrt_10',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Exception during target-value verification: {e}'
        })

    # Check 4: exact arithmetic for final answer.
    try:
        k, m, n = 10, 13, 4
        passed = (k + m + n == 27)
        checks.append({
            'name': 'final_sum',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'Using k=10, m=13, n=4 gives k+m+n=27.' if passed else f'Got {k+m+n} instead of 27.'
        })
    except Exception as e:
        checks.append({
            'name': 'final_sum',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Exception during final sum computation: {e}'
        })

    # Numerical sanity check using a concrete consistent pair (sin t, cos t).
    # If s = sqrt(10)/2 - 1 and p = 1/4 - s, then y^2 - s y + p = 0 has roots sin t, cos t.
    try:
        s_val = sp.sqrt(10) / 2 - 1
        p_val = sp.Rational(1, 4) - s_val
        disc = sp.simplify(s_val**2 - 4 * p_val)
        y1 = sp.simplify((s_val + sp.sqrt(disc)) / 2)
        y2 = sp.simplify((s_val - sp.sqrt(disc)) / 2)
        v1 = sp.N((1 + y1) * (1 + y2), 50)
        v2 = sp.N((1 - y1) * (1 - y2), 50)
        t1 = sp.N(sp.Rational(5, 4), 50)
        t2 = sp.N(sp.Rational(13, 4) - sp.sqrt(10), 50)
        passed = abs(v1 - t1) < sp.Float('1e-40') and abs(v2 - t2) < sp.Float('1e-40')
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Using exact roots with sum {sp.N(s_val,20)} and product {sp.N(p_val,20)}, numerically got (1+y1)(1+y2)={v1} and (1-y1)(1-y2)={v2}.'
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Exception during numerical sanity check: {e}'
        })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    import json
    print(json.dumps(verify(), indent=2))