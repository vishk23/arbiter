from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, expand, Eq


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: algebraic identity over integers/reals encoded in kdrag.
    x = Int('x')
    lhs = (x + 1) * (x + 1) * x
    rhs = x**3 + 2*x**2 + x
    try:
        proof = kd.prove(ForAll([x], lhs == rhs))
        checks.append({
            'name': 'kdrag_expand_identity',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {proof}',
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'kdrag_expand_identity',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {type(e).__name__}: {e}',
        })

    # Symbolic sanity check using SymPy expansion.
    xs = Symbol('x')
    sym_lhs = expand((xs + 1)**2 * xs)
    sym_rhs = xs**3 + 2*xs**2 + xs
    sym_passed = Eq(sym_lhs, sym_rhs)
    checks.append({
        'name': 'sympy_expand_sanity',
        'passed': bool(sym_passed),
        'backend': 'sympy',
        'proof_type': 'numerical',
        'details': f'expand((x+1)^2*x) -> {sym_lhs}, expected {sym_rhs}',
    })
    proved = proved and bool(sym_passed)

    # Numerical sanity check at a concrete value.
    val = 3
    lhs_num = (val + 1)**2 * val
    rhs_num = val**3 + 2*val**2 + val
    num_passed = lhs_num == rhs_num
    checks.append({
        'name': 'numerical_substitution_x_eq_3',
        'passed': num_passed,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'At x=3, lhs={lhs_num}, rhs={rhs_num}',
    })
    proved = proved and num_passed

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)