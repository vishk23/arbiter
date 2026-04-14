from sympy import (
    symbols,
    cos,
    pi,
    Rational,
    simplify,
    N,
)
from sympy.polys.numberfields import minimal_polynomial


def _check_symbolic_identity():
    x = symbols('x')
    expr = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7) - Rational(1, 2)
    try:
        mp = minimal_polynomial(expr, x)
        passed = (mp == x)
        return {
            'name': 'exact_trig_identity_via_minimal_polynomial',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'minimal_polynomial(expr, x) = {mp}'
        }
    except Exception as e:
        return {
            'name': 'exact_trig_identity_via_minimal_polynomial',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'exception during minimal_polynomial computation: {e}'
        }


def _check_hint_rewrite_symbolically():
    expr = simplify(cos(pi/7) - cos(2*pi/7) + cos(3*pi/7) - (cos(pi/7) + cos(3*pi/7) + cos(5*pi/7)))
    passed = (expr == 0)
    return {
        'name': 'rewrite_minus_cos_2pi7_as_plus_cos_5pi7',
        'passed': bool(passed),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'simplified difference = {expr}'
    }


def _check_numerical_sanity():
    lhs = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7)
    val = N(lhs, 50)
    diff = N(lhs - Rational(1, 2), 50)
    passed = abs(float(diff)) < 1e-12
    return {
        'name': 'numerical_sanity_50_digits',
        'passed': bool(passed),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'lhs ≈ {val}, lhs - 1/2 ≈ {diff}'
    }


def verify():
    checks = [
        _check_symbolic_identity(),
        _check_hint_rewrite_symbolically(),
        _check_numerical_sanity(),
    ]
    proved = all(c['passed'] for c in checks) and any(
        c['passed'] and c['proof_type'] in ('certificate', 'symbolic_zero') for c in checks
    )
    return {
        'proved': bool(proved),
        'checks': checks,
    }


if __name__ == '__main__':
    import json
    print(json.dumps(verify(), indent=2, default=str))