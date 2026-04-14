from math import isfinite
import sympy as sp


def verify():
    checks = []
    proved = True

    # ---------------------------------------------------------------------
    # Check 1: symbolic identity via SymPy simplification
    # We verify that the proposed answer matches the expression exactly.
    # ---------------------------------------------------------------------
    x = sp.Symbol('x', positive=True)
    expr = sp.sqrt(sp.log(6, 2) + sp.log(6, 3))
    proposed = sp.sqrt(sp.log(3, 2)) + sp.sqrt(sp.log(2, 3))
    symbolic_diff = sp.simplify(expr - proposed)
    passed_symbolic = symbolic_diff == 0
    checks.append({
        'name': 'symbolic_identity',
        'passed': bool(passed_symbolic),
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': f'simplify(expr - proposed) -> {symbolic_diff!r}'
    })
    proved = proved and passed_symbolic

    # ---------------------------------------------------------------------
    # Check 2: verified algebraic certificate for an equivalent identity.
    # Let a = log_2(3). Then log_3(2) = 1/a, and the target simplifies to
    # sqrt(a) + 1/sqrt(a). We certify the square identity symbolically.
    # ---------------------------------------------------------------------
    a = sp.Symbol('a', positive=True)
    lhs = (sp.sqrt(a) + 1 / sp.sqrt(a))**2
    rhs = a + 2 + 1 / a
    cert = sp.simplify(lhs - rhs)
    passed_cert = cert == 0
    checks.append({
        'name': 'algebraic_square_certificate',
        'passed': bool(passed_cert),
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': f'simplify((sqrt(a)+1/sqrt(a))**2 - (a+2+1/a)) -> {cert!r}'
    })
    proved = proved and passed_cert

    # ---------------------------------------------------------------------
    # Check 3: numerical sanity check at concrete values.
    # ---------------------------------------------------------------------
    num_expr = sp.N(expr, 40)
    num_proposed = sp.N(proposed, 40)
    passed_num = abs(complex(num_expr) - complex(num_proposed)) < 1e-30
    checks.append({
        'name': 'numerical_sanity',
        'passed': bool(passed_num),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'expr={num_expr}, proposed={num_proposed}'
    })
    proved = proved and passed_num

    return {
        'proved': bool(proved),
        'checks': checks,
    }


if __name__ == '__main__':
    result = verify()
    print(result)