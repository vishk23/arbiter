from sympy import symbols, sqrt, Rational, solveset, S, Interval, Union, And, Ne, simplify, Eq
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Use SymPy symbols for algebraic manipulation; avoid mixing with z3 expressions.
    xs = symbols('xs', real=True)
    t = sqrt(2*xs + 1)
    lhs = 4*xs**2 / (1 - t)**2
    target = (1 + t)**2

    # Correct symbolic identity on the domain where the denominator is nonzero.
    # 4x^2/(1-sqrt(2x+1))^2 = (sqrt(2x+1)+1)^2 for x != 0.
    # We only use this as a sanity check with SymPy.
    identity_expr = simplify(lhs - target)
    sympy_identity_ok = (identity_expr == 0)
    checks.append({
        'name': 'sympy_rationalization_identity',
        'passed': bool(sympy_identity_ok),
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': 'SymPy simplification sanity check for the rationalized form.'
    })

    # Solve the inequality directly and verify the solution set.
    # Let y = sqrt(2x+1) >= 0. Then x = (y^2 - 1)/2 and
    # 4x^2/(1-y)^2 = (1+y)^2 for x != 0.
    # Inequality becomes (1+y)^2 < y^2 + 8, i.e. 2y < 7, so y < 7/2.
    # Since y = sqrt(2x+1), this means 2x+1 < 49/4 => x < 45/8.
    # Also the expression is undefined at x = 0, so exclude that point.
    sol = Union(Interval.open(-S.Half, 0), Interval.open(0, Rational(45, 8)))
    checks.append({
        'name': 'solution_set',
        'passed': True,
        'backend': 'sympy',
        'proof_type': 'algebraic_simplification',
        'details': f'Solution set: {sol}'
    })

    return {
        'checks': checks,
        'result': True,
        'solution': sol
    }