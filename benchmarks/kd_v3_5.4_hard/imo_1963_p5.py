from __future__ import annotations

from typing import Any, Dict, List


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Check 1: rigorous symbolic proof via minimal polynomial
    try:
        import sympy as sp

        x = sp.Symbol('x')
        expr = sp.cos(sp.pi/7) - sp.cos(2*sp.pi/7) + sp.cos(3*sp.pi/7) - sp.Rational(1, 2)
        mp = sp.minimal_polynomial(expr, x)
        passed = sp.expand(mp) == x
        checks.append({
            'name': 'sympy_minimal_polynomial_zero',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'minimal_polynomial(expr - 1/2, x) = {sp.sstr(mp)}; equality to x proves expr - 1/2 = 0 exactly.'
        })
    except Exception as e:
        checks.append({
            'name': 'sympy_minimal_polynomial_zero',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy symbolic proof failed with exception: {type(e).__name__}: {e}'
        })

    # Check 2: exact symbolic simplification sanity check
    try:
        import sympy as sp

        expr = sp.cos(sp.pi/7) - sp.cos(2*sp.pi/7) + sp.cos(3*sp.pi/7)
        simplified = sp.simplify(expr - sp.Rational(1, 2))
        passed = simplified == 0
        checks.append({
            'name': 'sympy_exact_simplify',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'simplify(expr - 1/2) returned {sp.sstr(simplified)}.'
        })
    except Exception as e:
        checks.append({
            'name': 'sympy_exact_simplify',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy simplify check failed with exception: {type(e).__name__}: {e}'
        })

    # Check 3: rigorous exact proof of the auxiliary identity cos(5π/7) = -cos(2π/7)
    try:
        import sympy as sp

        x = sp.Symbol('x')
        aux = sp.cos(5*sp.pi/7) + sp.cos(2*sp.pi/7)
        mp = sp.minimal_polynomial(aux, x)
        passed = sp.expand(mp) == x
        checks.append({
            'name': 'sympy_aux_cos_relation',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'minimal_polynomial(cos(5π/7)+cos(2π/7), x) = {sp.sstr(mp)}.'
        })
    except Exception as e:
        checks.append({
            'name': 'sympy_aux_cos_relation',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Auxiliary symbolic proof failed with exception: {type(e).__name__}: {e}'
        })

    # Check 4: numerical sanity check
    try:
        import sympy as sp

        expr = sp.cos(sp.pi/7) - sp.cos(2*sp.pi/7) + sp.cos(3*sp.pi/7)
        val = sp.N(expr, 80)
        diff = sp.N(expr - sp.Rational(1, 2), 80)
        passed = abs(float(diff)) < 1e-30
        checks.append({
            'name': 'numerical_sanity',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'80-digit evaluation gives expr = {val}, expr - 1/2 = {diff}.'
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed with exception: {type(e).__name__}: {e}'
        })

    proved = all(check['passed'] for check in checks) and any(
        check['passed'] and check['proof_type'] in ('certificate', 'symbolic_zero') for check in checks
    )

    return {
        'proved': bool(proved),
        'checks': checks,
    }


if __name__ == '__main__':
    import json
    print(json.dumps(verify(), indent=2))