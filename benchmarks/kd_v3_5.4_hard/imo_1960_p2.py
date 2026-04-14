import traceback
import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, Rational, sqrt, Interval, Union, FiniteSet, solveset, S, simplify


def verify():
    checks = []

    # Solve the inequality directly with SymPy over the reals.
    # Domain constraints of the original expression:
    #   2x+1 >= 0  -> x >= -1/2
    #   1 - sqrt(2x+1) != 0 -> x != 0
    # Rationalizing for x != 0 gives
    #   4x^2 / (1 - sqrt(2x+1))^2 = (1 + sqrt(2x+1))^2.
    # Then the inequality becomes
    #   (1 + sqrt(2x+1))^2 < 2x + 9
    #   2x + 2 + 2*sqrt(2x+1) < 2x + 9
    #   2*sqrt(2x+1) < 7
    #   x < 45/8,
    # together with x >= -1/2 and x != 0.
    # Hence the solution set is [-1/2, 0) U (0, 45/8).
    try:
        x = Symbol('x', real=True)
        sol = solveset(4*x**2 / (1 - sqrt(2*x + 1))**2 < 2*x + 9, x, domain=S.Reals)
        expected = Union(Interval(Rational(-1, 2), 0, left_open=False, right_open=True),
                         Interval(0, Rational(45, 8), left_open=True, right_open=True))
        passed = (sol == expected)
        checks.append({
            'name': 'sympy_original_inequality_solution_set',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic',
            'details': f'solveset returned {sol}; expected {expected}.'
        })
    except Exception as e:
        checks.append({
            'name': 'sympy_original_inequality_solution_set',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic',
            'details': f'Exception during solveset: {e}\n{traceback.format_exc()}'
        })

    # Check the exact algebraic simplification after substituting t = sqrt(2x+1).
    # For x != 0, with t = sqrt(2x+1), we have x = (t^2 - 1)/2 and
    #   4x^2/(1-t)^2 = (t+1)^2.
    try:
        t = Symbol('t', real=True)
        x_sub = (t**2 - 1) / 2
        expr = simplify(4 * x_sub**2 / (1 - t)**2 - (t + 1)**2)
        passed = (expr == 0)
        checks.append({
            'name': 'sympy_substitution_identity_t_not_1',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic',
            'details': f'Simplified expression: {expr}'
        })
    except Exception as e:
        checks.append({
            'name': 'sympy_substitution_identity_t_not_1',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic',
            'details': f'Exception during simplification: {e}\n{traceback.format_exc()}'
        })

    # Z3/kdrag sanity checks on representative points.
    try:
        xr = Real('xr')
        orig = lambda v: (4*v*v) / ((1 - Sqrt(2*v + 1))*(1 - Sqrt(2*v + 1))) < 2*v + 9

        kd.prove(orig(RealVal('-1/2')))
        kd.prove(orig(RealVal('1/2')))
        kd.prove(orig(RealVal('5')))
        checks.append({
            'name': 'kdrag_sample_points',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'smt',
            'details': 'Verified sample points x=-1/2 and x=1/2 satisfy the inequality, and x=5 also satisfies it.'
        })
    except kd.kernel.LemmaError as e:
        checks.append({
            'name': 'kdrag_sample_points',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'smt',
            'details': f'LemmaError: {e}'
        })
    except Exception as e:
        checks.append({
            'name': 'kdrag_sample_points',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'smt',
            'details': f'Exception: {e}\n{traceback.format_exc()}'
        })

    # Explicitly verify the boundary behavior: x=0 is excluded (denominator zero), x=45/8 is not included.
    try:
        x = Symbol('x', real=True)
        denom_at_0 = simplify((1 - sqrt(2*0 + 1))**2)
        boundary_expr = simplify(4*(Rational(45, 8))**2 / (1 - sqrt(2*Rational(45, 8) + 1))**2 - (2*Rational(45, 8) + 9))
        passed = (denom_at_0 == 0 and boundary_expr == 0)
        checks.append({
            'name': 'sympy_boundary_checks',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic',
            'details': f'denominator at x=0 -> {denom_at_0}; expression minus RHS at x=45/8 -> {boundary_expr}'
        })
    except Exception as e:
        checks.append({
            'name': 'sympy_boundary_checks',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic',
            'details': f'Exception during boundary checks: {e}\n{traceback.format_exc()}'
        })

    return checks


if __name__ == '__main__':
    import json
    print(json.dumps({'checks': verify()}, indent=2))