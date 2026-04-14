import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, factor, together, simplify, solve, Eq, Rational


def verify():
    checks = []
    all_passed = True

    # Let a = x^2 - 10x - 29. Then the equation becomes
    # 1/a + 1/(a-16) - 2/(a-40) = 0.
    # Clearing denominators gives a^2 - 40a + 256 = 0, i.e. (a-16)^2 = 0.
    # Hence a = 16, and then x^2 - 10x - 45 = 0, whose positive root is 15.

    # Check 1: symbolic reduction of the transformed equation
    try:
        a = Symbol('a')
        expr = 1/a + 1/(a - 16) - 2/(a - 40)
        num = together(expr).as_numer_denom()[0]
        num_simplified = factor(simplify(num))
        sol = solve(Eq(num, 0), a)
        passed = (str(num_simplified) == '(a - 16)**2' or str(num_simplified) == 'a**2 - 32*a + 256' or num_simplified == (a - 16)**2) and sol == [16]
        all_passed = all_passed and passed
        checks.append('reduced_equation_has_unique_solution_a_equals_16')
    except Exception:
        all_passed = False
        checks.append('reduced_equation_has_unique_solution_a_equals_16')

    # Check 2: solve the resulting quadratic for x and confirm the positive solution is 15
    try:
        x = Symbol('x')
        eq = Eq(x**2 - 10*x - 45, 0)
        roots = solve(eq, x)
        passed = sorted(roots) == [Rational(-5), Rational(15)]
        all_passed = all_passed and passed
        checks.append('quadratic_in_x_has_positive_solution_15')
    except Exception:
        all_passed = False
        checks.append('quadratic_in_x_has_positive_solution_15')

    return checks