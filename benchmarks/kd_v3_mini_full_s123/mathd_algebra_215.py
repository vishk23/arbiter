from sympy import symbols, Eq, solve, simplify
import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify():
    checks = []

    # Solve the equation exactly and check the sum of the two solutions.
    x = symbols('x')
    sols = solve(Eq((x + 3)**2, 121), x)
    sum_sols = simplify(sum(sols))
    checks.append({
        "name": "exact_solution_sum",
        "passed": sum_sols == -6,
        "backend": "sympy",
        "proof_type": "computation",
        "details": f"solutions={sols}, sum={sum_sols}",
    })

    # Direct algebraic check: expand the equation and factor the polynomial.
    # (x + 3)^2 = 121  <=>  x^2 + 6x - 112 = 0.
    # The roots are 8 and -14, whose sum is -6.
    x2 = symbols('x2')
    poly_sols = solve(Eq(x2**2 + 6*x2 - 112, 0), x2)
    poly_sum = simplify(sum(poly_sols))
    checks.append({
        "name": "polynomial_root_sum",
        "passed": poly_sum == -6,
        "backend": "sympy",
        "proof_type": "computation",
        "details": f"roots={poly_sols}, sum={poly_sum}",
    })

    return checks