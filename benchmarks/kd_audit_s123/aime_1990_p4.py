from __future__ import annotations

from typing import Dict, List, Any

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Real, ForAll, Implies, And
except Exception:  # pragma: no cover
    kd = None


x = sp.Symbol('x', real=True)
a = sp.Symbol('a', real=True)


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: Verified symbolic proof with kdrag that the transformed equation implies a = 10.
    if kd is None:
        checks.append({
            'name': 'kdrag_transformed_equation_implies_a_equals_10',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kdrag is unavailable in this environment, so no certificate could be produced.',
        })
        proved = False
    else:
        A = Real('A')
        try:
            proof1 = kd.prove(
                ForAll([A], Implies((A - 16) * (A - 40) + A * (A - 40) - 2 * A * (A - 16) == 0, A == 10))
            )
            checks.append({
                'name': 'kdrag_transformed_equation_implies_a_equals_10',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Verified by kdrag certificate: {proof1}',
            })
        except Exception as e:
            checks.append({
                'name': 'kdrag_transformed_equation_implies_a_equals_10',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kdrag proof failed: {e}',
            })
            proved = False

    # Check 2: SymPy exact algebraic verification that the derived quadratic has roots 13 and -3.
    try:
        factor = sp.factor(x**2 - 10*x - 39)
        symbolic_ok = sp.expand(factor - (x - 13) * (x + 3)) == 0
        passed = symbolic_ok and factor == (x - 13) * (x + 3)
        checks.append({
            'name': 'sympy_factorization_of_quadratic',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'factor(x^2 - 10*x - 39) = {factor}; expected (x - 13)(x + 3).',
        })
        if not passed:
            proved = False
    except Exception as e:
        checks.append({
            'name': 'sympy_factorization_of_quadratic',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy factorization failed: {e}',
        })
        proved = False

    # Check 3: Numerical sanity check at x = 13.
    try:
        xv = sp.Integer(13)
        expr = 1 / (xv**2 - 10*xv - 29) + 1 / (xv**2 - 10*xv - 45) - 2 / (xv**2 - 10*xv - 69)
        numeric_pass = sp.simplify(expr) == 0
        checks.append({
            'name': 'numerical_sanity_at_x_equals_13',
            'passed': numeric_pass,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Evaluated expression at x=13 to {sp.simplify(expr)}.',
        })
        if not numeric_pass:
            proved = False
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_at_x_equals_13',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical evaluation failed: {e}',
        })
        proved = False

    # Check 4: Direct symbolic reduction from the given equation to a = 10 using exact algebra.
    try:
        expr_a = sp.simplify(1 / a + 1 / (a - 16) - 2 / (a - 40))
        numerator = sp.factor(sp.together(expr_a).as_numer_denom()[0])
        passed = sp.expand(numerator + 64 * (a - 10)) == 0
        checks.append({
            'name': 'symbolic_reduction_to_a_equals_10',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Numerator after clearing denominators is {numerator}; equivalent to -64*(a-10).',
        })
        if not passed:
            proved = False
    except Exception as e:
        checks.append({
            'name': 'symbolic_reduction_to_a_equals_10',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Symbolic reduction failed: {e}',
        })
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)