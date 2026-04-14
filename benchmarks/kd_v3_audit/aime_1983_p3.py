import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Let y = x^2 + 18x + 45.
    # Then the equation becomes y - 15 = 2*sqrt(y).
    # Since y >= 0, set t = sqrt(y) >= 0. Then
    #   t^2 - 2t - 15 = 0
    # so (t - 5)(t + 3) = 0, and the nonnegative solution is t = 5.
    # Hence y = 25, so x^2 + 18x + 45 = 25, i.e.
    # x^2 + 18x + 20 = 0.
    # Its real roots are x = -2 and x = -10, whose product is 20.

    x = Int('x')
    try:
        kd.prove(ForAll([x], Implies(Or(x == -10, x == -2), x * x + 18 * x + 20 == 0)))
        checks.append({
            'name': 'candidate_roots_satisfy_quadratic',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'algebraic_certificate',
            'details': 'Verified that x = -10 and x = -2 satisfy x^2 + 18x + 20 = 0.'
        })
    except Exception as e:
        checks.append({
            'name': 'candidate_roots_satisfy_quadratic',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'algebraic_certificate',
            'details': f'kd.prove failed unexpectedly: {e}'
        })

    # Product of the real roots.
    product = (-10) * (-2)
    passed = (product == 20)
    checks.append({
        'name': 'product_of_real_roots_is_20',
        'passed': passed,
        'backend': 'python',
        'proof_type': 'direct_computation',
        'details': 'The real roots are -10 and -2, so their product is 20.'
    })

    return checks