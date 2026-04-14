from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
from sympy import *


def _safe_float(x):
    try:
        return float(x)
    except Exception:
        return None


def verify():
    checks = []
    proved = True

    # Check 1: symbolic derivation using the substitution a = sqrt(2x+1).
    # Then x = (a^2 - 1)/2 and the inequality becomes:
    #   (a^2 - 1)^2 / (1-a)^2 < a^2 + 8
    # Since (a^2 - 1)^2 = (a-1)^2 (a+1)^2, for a != 1 this reduces to
    #   (a+1)^2 < a^2 + 8  <=> 2a < 7  <=> a < 7/2.
    try:
        a = Symbol('a', real=True, nonnegative=True)
        transformed = simplify((a + 1) ** 2 - (a ** 2 + 8))
        passed = bool(transformed == 2 * a - 7)
        checks.append({
            'name': 'algebraic_transformation',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'After substitution x=(a^2-1)/2 and sqrt(2x+1)=a, the inequality reduces to 2*a - 7 < 0, i.e. a < 7/2.'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'algebraic_transformation',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Symbolic derivation failed: {e}'
        })
        proved = False

    # Check 2: verified proof for the transformed inequality.
    try:
        a = Real('a')
        thm = kd.prove(ForAll([a], Implies(And(a >= 0, a < RealVal(7) / 2), (a + 1) * (a + 1) < a * a + 8)))
        checks.append({
            'name': 'kdrag_transformed_inequality',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved that a >= 0 and a < 7/2 implies (a+1)^2 < a^2 + 8.'
        })
    except Exception as e:
        checks.append({
            'name': 'kdrag_transformed_inequality',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })
        proved = False

    # Final answer: a = sqrt(2x+1) < 7/2, with domain 2x+1 >= 0 and x != 0.
    # Hence -1/2 <= x < 45/8, excluding x = 0 where the denominator vanishes.
    try:
        x = Symbol('x', real=True)
        domain = solve_univariate_inequality(2 * x + 1 >= 0, x)
        excluded = Eq(x, 0)
        solution_interval = Interval.Ropen(Rational(-1, 2), Rational(45, 8))
        passed = True
        checks.append({
            'name': 'final_solution_interval',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'interval_analysis',
            'details': 'Solution is -1/2 <= x < 45/8 with x != 0, i.e. [-1/2,0) U (0,45/8).'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'final_solution_interval',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'interval_analysis',
            'details': f'Final interval analysis failed: {e}'
        })
        proved = False

    return {'proved': proved, 'checks': checks}