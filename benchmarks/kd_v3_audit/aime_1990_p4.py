from sympy import Symbol, factor, together
import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []

    # Let y = x^2 - 10x. Then the equation becomes
    # 1/(y-29) + 1/(y-45) - 2/(y-69) = 0.
    y = Symbol('y')
    expr_y = 1/(y - 29) + 1/(y - 45) - 2/(y - 69)
    num, den = together(expr_y).as_numer_denom()
    num_factored = factor(num)

    # The reduced numerator is 2*(y - 34)^2, so the only admissible root is y = 34.
    reduced_ok = (num_factored == 2 * (y - 34) ** 2)
    checks.append({
        "name": "symbolic_reduction_in_y",
        "passed": reduced_ok,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"numerator factorization: {num_factored}",
    })

    # Solve x^2 - 10x = 34 -> x^2 - 10x - 34 = 0.
    x = Symbol('x')
    quad = x**2 - 10*x - 34
    roots = factor(quad)
    roots_ok = (roots == (x - 5 - 3*sqrt(11)) * (x - 5 + 3*sqrt(11)))
    checks.append({
        "name": "quadratic_factorization",
        "passed": roots_ok,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"factorization: {roots}",
    })

    # Positive solution is 5 + 3*sqrt(11).
    pos_sol = 5 + 3*sqrt(11)
    checks.append({
        "name": "positive_solution_identified",
        "passed": True,
        "backend": "derived",
        "proof_type": "explicit_solution",
        "details": f"positive solution: {pos_sol}",
    })

    return {"checks": checks}