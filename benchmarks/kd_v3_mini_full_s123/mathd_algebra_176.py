from __future__ import annotations

from typing import Any, Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import Real, ForAll, Not
except Exception:  # pragma: no cover
    kd = None
    Real = None
    ForAll = None
    Not = None


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: Verified symbolic proof with SymPy expansion.
    x = sp.symbols('x')
    lhs = sp.expand((x + 1) ** 2 * x)
    rhs = x ** 3 + 2 * x ** 2 + x
    sympy_ok = sp.expand(lhs - rhs) == 0
    checks.append(
        {
            'name': 'sympy_expand_matches_target',
            'passed': bool(sympy_ok),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Expanded lhs - rhs simplifies to {sp.expand(lhs - rhs)}.',
        }
    )
    proved = proved and bool(sympy_ok)

    # Check 2: Numerical sanity check at a concrete value.
    x_val = 3
    lhs_num = ((x_val + 1) ** 2) * x_val
    rhs_num = x_val ** 3 + 2 * x_val ** 2 + x_val
    num_ok = lhs_num == rhs_num
    checks.append(
        {
            'name': 'numerical_sanity_check_at_x_3',
            'passed': bool(num_ok),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'lhs={lhs_num}, rhs={rhs_num} at x={x_val}.',
        }
    )
    proved = proved and bool(num_ok)

    # Check 3: Verified certificate with kdrag for polynomial identity.
    if kd is not None:
        xr = Real('x')
        try:
            thm = kd.prove((xr + 1) * (xr + 1) * xr == xr ** 3 + 2 * xr ** 2 + xr)
            kd_ok = True
            details = f'kd.prove returned certificate: {thm!r}'
        except Exception as e:
            kd_ok = False
            details = f'kdrag proof failed: {type(e).__name__}: {e}'
    else:
        kd_ok = False
        details = 'kdrag is unavailable in this environment.'

    checks.append(
        {
            'name': 'kdrag_polynomial_identity_certificate',
            'passed': bool(kd_ok),
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': details,
        }
    )
    proved = proved and bool(kd_ok)

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)