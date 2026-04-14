from sympy import Symbol, binomial, expand, Integer

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Check 1: Verified proof for the key number-theoretic claim.
    # For every prime p and integer a, p divides a^p - a.
    p = Int('p')
    a = Int('a')
    thm = None
    try:
        thm = kd.prove(
            ForAll([p, a],
                Implies(
                    And(p > 1, a >= 0, Not(Exists([Int('q')], And(Int('q') > 1, Int('q') < p, p % Int('q') == 0)))),
                    (a**p - a) % p == 0
                )
            )
        )
        checks.append({
            'name': 'fermat_little_theorem_divisibility',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm)
        })
    except Exception as e:
        checks.append({
            'name': 'fermat_little_theorem_divisibility',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof attempt failed: {type(e).__name__}: {e}'
        })

    # Check 2: A symbolic sanity check of the binomial expansion step for a concrete prime p=5.
    x = Symbol('x')
    expr = expand((x + 1)**5 - (x + 1) - (x**5 - x))
    coeffs_ok = all(int(c) % 5 == 0 for c in expr.as_poly(x).all_coeffs())
    checks.append({
        'name': 'binomial_step_p_equals_5',
        'passed': bool(coeffs_ok),
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': f'Expanded difference: {expr}; all coefficients divisible by 5: {coeffs_ok}'
    })

    # Check 3: Numerical sanity checks for small primes and values.
    nums = [(2, 1), (2, 7), (3, 4), (5, 9), (7, 3)]
    numeric_ok = all(((a0**p0 - a0) % p0) == 0 for p0, a0 in nums)
    checks.append({
        'name': 'small_numeric_sanity',
        'passed': bool(numeric_ok),
        'backend': 'python',
        'proof_type': 'numeric_check',
        'details': f'Checked pairs: {nums}; all passed: {numeric_ok}'
    })

    return checks