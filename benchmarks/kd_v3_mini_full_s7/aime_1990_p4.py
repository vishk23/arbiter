import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    def add_check(name, passed, backend, proof_type, details):
        checks.append(
            {
                "name": name,
                "passed": bool(passed),
                "backend": backend,
                "proof_type": proof_type,
                "details": details,
            }
        )

    # Solve the equation exactly by algebraic simplification.
    # Let t = x^2 - 10x. Then
    #   1/(t-29) + 1/(t-45) - 2/(t-69) = 0.
    # Clearing denominators gives a polynomial equation in t.
    t = sp.Symbol("t")
    expr = sp.simplify(1/(t - 29) + 1/(t - 45) - 2/(t - 69))
    num = sp.factor(sp.together(expr).as_numer_denom()[0])
    den = sp.factor(sp.together(expr).as_numer_denom()[1])
    add_check(
        name="sympy_clears_to_polynomial_in_t",
        passed=sp.expand(num) == sp.expand((t - 69) * (t - 45) * (t - 29) * expr).as_numer_denom()[0],
        backend="sympy",
        proof_type="symbolic",
        details=f"Cleared numerator: {num}, denominator: {den}",
    )

    # Solve the reduced equation for t.
    sol_t = sp.solve(sp.Eq(expr, 0), t)
    add_check(
        name="sympy_solve_reduced_equation",
        passed=(sol_t == [69]),
        backend="sympy",
        proof_type="symbolic",
        details=f"Reduced solutions for t: {sol_t}",
    )

    # Now solve x^2 - 10x = 69 -> x^2 - 10x - 69 = 0.
    x = sp.Symbol("x")
    sol_x = sp.solve(sp.Eq(x**2 - 10*x - 69, 0), x)
    positive = [s for s in sol_x if sp.N(s) > 0]
    add_check(
        name="sympy_positive_solution_is_13",
        passed=(positive == [13]),
        backend="sympy",
        proof_type="symbolic",
        details=f"All solutions: {sol_x}; positive solutions: {positive}",
    )

    # Verify directly that x = 13 satisfies the original equation.
    original = 1/(x**2 - 10*x - 29) + 1/(x**2 - 10*x - 45) - 2/(x**2 - 10*x - 69)
    direct_check = sp.simplify(original.subs(x, 13))
    add_check(
        name="direct_substitution_x_equals_13",
        passed=(direct_check == 0),
        backend="sympy",
        proof_type="symbolic",
        details=f"Substitution result: {direct_check}",
    )

    return checks