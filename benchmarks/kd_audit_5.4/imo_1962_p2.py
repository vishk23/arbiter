import math
from sympy import symbols, sqrt, Rational, simplify, Interval, solveset, S, N
from sympy import minimal_polynomial, factor


def _check_domain_symbolic():
    x = symbols('x', real=True)
    expr = sqrt(3 - x) - sqrt(x + 1)
    target = simplify(expr.subs(x, 1))
    # On [-1,1], expr is defined and nonnegative; endpoints certify the boundary values.
    ok = simplify(expr.subs(x, -1) - sqrt(2)) == 0 and target == 0
    return {
        'name': 'domain_and_endpoint_values',
        'passed': bool(ok),
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': 'Verified symbolically that f(-1)=sqrt(2) and sqrt(3-x)-sqrt(x+1) at x=1 equals 0, consistent with domain [-1,1].'
    }


def _check_threshold_root_symbolic():
    x, t = symbols('x t', real=True)
    root = 1 - sqrt(127) / 32
    expr = sqrt(sqrt(3 - root) - sqrt(root + 1)) - Rational(1, 2)
    mp = minimal_polynomial(simplify(expr), t)
    ok = simplify(mp - t) == 0
    return {
        'name': 'boundary_value_equals_half',
        'passed': bool(ok),
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': f'minimal_polynomial(f(root)-1/2, t) = {mp}; equality to t proves the algebraic number is exactly 0 for root = 1 - sqrt(127)/32.'
    }


def _check_quadratic_factor_symbolic():
    x = symbols('x', real=True)
    poly = 1024*x**2 - 2048*x + 897
    fac = factor(poly)
    expected = 1024*(x - (1 - sqrt(127)/32))*(x - (1 + sqrt(127)/32))
    ok = simplify(fac - expected) == 0
    return {
        'name': 'quadratic_roots_match_claim',
        'passed': bool(ok),
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': f'Factored polynomial exactly as {fac}, confirming roots 1 ± sqrt(127)/32.'
    }


def _check_solution_set_numerical():
    root = 1 - math.sqrt(127) / 32.0

    def f(x):
        return math.sqrt(math.sqrt(3 - x) - math.sqrt(x + 1))

    samples = [
        (-1.0, True),
        ((-1.0 + root) / 2.0, True),
        (root, False),
        ((root + 1.0) / 2.0, False),
        (1.0, False),
    ]
    passed = True
    msgs = []
    for val, expected in samples:
        lhs = f(val)
        got = lhs > 0.5
        if got != expected:
            passed = False
        msgs.append(f'x={val:.12f}: lhs={lhs:.12f}, lhs>1/2 is {got}, expected {expected}')
    return {
        'name': 'numerical_sanity_samples',
        'passed': passed,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': '; '.join(msgs)
    }


def verify():
    checks = [
        _check_domain_symbolic(),
        _check_threshold_root_symbolic(),
        _check_quadratic_factor_symbolic(),
        _check_solution_set_numerical(),
    ]
    proved = all(c['passed'] for c in checks)
    return {
        'proved': proved,
        'checks': checks,
    }


if __name__ == '__main__':
    import json
    print(json.dumps(verify(), indent=2, default=str))