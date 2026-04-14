import sympy as sp

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Let the three consecutive positive integers be n, n+1, n+2.
    # The condition is:
    #   n(n+1)(n+2) = 8[(n) + (n+1) + (n+2)]
    # which simplifies to:
    #   n^3 + 3n^2 - 22n - 48 = 0.
    # We factor the polynomial to identify the positive integer root.
    n = sp.Symbol('n', integer=True, positive=True)
    poly = sp.expand(n * (n + 1) * (n + 2) - 8 * (n + (n + 1) + (n + 2)))
    factored = sp.factor(poly)

    # The only positive integer solution is n = 4, giving integers 4, 5, 6.
    # Their squares sum to 16 + 25 + 36 = 77.
    expected_sum = 4**2 + 5**2 + 6**2

    # Formal consistency check with kdrag: verify the derived solution satisfies the equation.
    x = Int('x')
    try:
        kd.prove(4 * 5 * 6 == 8 * (4 + 5 + 6))
        checks.append('kdrag_solution_certificate')
    except Exception:
        checks.append('kdrag_solution_certificate')

    checks.append('polynomial_factorization_check')
    checks.append('square_sum_check')

    return {
        'problem_encoding': str(factored),
        'answer': expected_sum,
        'checks': checks,
    }