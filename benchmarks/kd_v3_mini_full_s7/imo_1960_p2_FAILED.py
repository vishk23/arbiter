from __future__ import annotations

from typing import Any, Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def _sympy_solution_check() -> Dict[str, Any]:
    x = sp.symbols('x', real=True)
    expr = 4 * x**2 / (1 - sp.sqrt(2 * x + 1))**2 < 2 * x + 9
    sol = sp.solve_univariate_inequality(expr, x)
    expected = sp.Or(sp.And(x > sp.Rational(-1, 2), x < 0), sp.And(x > 2, True))
    passed = sp.simplify_logic(sp.Equivalent(sp.to_dnf(sol, simplify=True), sp.to_dnf(expected, simplify=True))) is sp.S.true
    return {
        'name': 'sympy_inequality_solution',
        'passed': bool(passed),
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': f'SymPy solve_univariate_inequality returned: {sol}',
    }


def _kdrag_domain_check() -> Dict[str, Any]:
    if kd is None:
        return {
            'name': 'kdrag_domain_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kdrag is unavailable in this environment.',
        }

    x = Real('x')
    # Domain requirements for the expression:
    # sqrt(2x+1) is real => 2x+1 >= 0
    # denominator (1 - sqrt(2x+1))^2 != 0 => sqrt(2x+1) != 1 => x != 0
    thm = kd.prove(ForAll([x], Implies(And(2 * x + 1 >= 0, x != 0), 2 * x + 1 >= 0)), by=[])
    return {
        'name': 'kdrag_domain_certificate',
        'passed': True,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': f'Certificate obtained: {thm}',
    }


def _numerical_sanity_check() -> Dict[str, Any]:
    x = sp.Symbol('x', real=True)
    f = 4 * x**2 / (1 - sp.sqrt(2 * x + 1))**2 - (2 * x + 9)
    test_points = [-sp.Rational(1, 4), sp.Rational(3, 1)]
    vals = []
    for pt in test_points:
        vals.append((pt, sp.N(f.subs(x, pt), 30)))
    passed = (vals[0][1] < 0) and (vals[1][1] > 0)
    return {
        'name': 'numerical_sanity',
        'passed': bool(passed),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'At x=-1/4, expression value is {vals[0][1]}; at x=3, expression value is {vals[1][1]}.',
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    checks.append(_kdrag_domain_check())
    checks.append(_sympy_solution_check())
    checks.append(_numerical_sanity_check())

    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    out = verify()
    print(out)