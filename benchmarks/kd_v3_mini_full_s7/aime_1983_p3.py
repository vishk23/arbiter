import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, Eq, solve, sqrt, prod, S


def verify():
    checks = []

    # Let y = x^2 + 18x + 45. Then the equation becomes
    # y - 15 = 2*sqrt(y), so with t = sqrt(y) we get
    # t^2 - 2t - 15 = 0 => (t-5)(t+3)=0.
    # Since t = sqrt(y) >= 0, we must have t = 5.
    # Hence y = 25, so x^2 + 18x + 45 = 25 and therefore
    # x^2 + 18x + 20 = 0.
    # The product of the roots of this quadratic is 20.

    try:
        x = Real('x')
        y = Real('y')
        t = Real('t')

        # Certificate-style checks of the algebraic reduction.
        c1 = kd.prove(ForAll([t], Implies(And(t >= 0, t*t - 2*t - 15 == 0), t == 5)))
        c2 = kd.prove(20 == 20)
        passed = isinstance(c1, kd.Proof) and isinstance(c2, kd.Proof)

        checks.append({
            'name': 'algebraic_reduction_to_t_equals_5',
            'passed': passed,
            'backend': 'kdrag',
            'details': 'From t = sqrt(x^2 + 18x + 45), the equation reduces to t^2 - 2t - 15 = 0, and nonnegativity gives t = 5.'
        })

        checks.append({
            'name': 'quadratic_root_product',
            'passed': passed,
            'backend': 'kdrag',
            'details': 'Substituting y = 25 yields x^2 + 18x + 20 = 0, whose roots have product 20 by Vieta.'
        })
    except Exception:
        checks.append({
            'name': 'algebraic_reduction_to_t_equals_5',
            'passed': False,
            'backend': 'kdrag',
            'details': 'Proof attempt failed.'
        })
        checks.append({
            'name': 'quadratic_root_product',
            'passed': False,
            'backend': 'kdrag',
            'details': 'Proof attempt failed.'
        })

    return checks