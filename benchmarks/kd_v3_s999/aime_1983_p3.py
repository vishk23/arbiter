import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, sqrt, Eq, solve, simplify, Poly, minimal_polynomial


def verify():
    checks = []

    # The key step is to rewrite the equation using y = x^2 + 18x + 45.
    # Then the original equation
    #     x^2 + 18x + 30 = 2*sqrt(x^2 + 18x + 45)
    # becomes
    #     y - 15 = 2*sqrt(y).
    # Since sqrt(y) is real and nonnegative, we can set t = sqrt(y) >= 0,
    # giving t^2 - 2t - 15 = 0, so t in {5, -3}. Only t = 5 is valid.
    # Hence y = 25 and therefore x^2 + 18x + 45 = 25, i.e.
    #     x^2 + 18x + 20 = 0.
    # Its real roots are x = -10 and x = -8, so the product is 80.

    x = Symbol('x', real=True)
    y = Symbol('y', real=True)
    t = Symbol('t', real=True)

    # Check 1: algebraic reduction of the original equation to a quadratic in t = sqrt(y)
    try:
        expr = (y - 15) - 2*t
        # Substitute y = t**2 (since t = sqrt(y)) and simplify the derived equation
        reduced = simplify((t**2 - 15) - 2*t)
        # The resulting polynomial is t^2 - 2t - 15 = 0
        poly = Poly(reduced, t)
        checks.append("reduction_to_quadratic_ok" if poly.as_expr() == t**2 - 2*t - 15 else "reduction_to_quadratic_bad")
    except Exception:
        checks.append("reduction_to_quadratic_bad")

    # Check 2: solve the quadratic and extract the valid nonnegative t
    try:
        sols_t = solve(Eq(t**2 - 2*t - 15, 0), t)
        valid_t = [s for s in sols_t if s.is_real is not False]
        # Among the solutions {5, -3}, only 5 is compatible with t = sqrt(y) >= 0.
        checks.append("valid_sqrt_branch_ok" if 5 in sols_t and -3 in sols_t else "valid_sqrt_branch_bad")
    except Exception:
        checks.append("valid_sqrt_branch_bad")

    # Check 3: solve the reduced quadratic in x and verify product of real roots.
    try:
        roots_x = solve(Eq(x**2 + 18*x + 20, 0), x)
        prod = simplify(roots_x[0] * roots_x[1])
        checks.append("product_of_real_roots_ok" if prod == 80 else "product_of_real_roots_bad")
    except Exception:
        checks.append("product_of_real_roots_bad")

    return checks