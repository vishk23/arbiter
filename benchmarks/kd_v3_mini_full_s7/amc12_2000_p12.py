import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, expand, minimal_polynomial


def verify():
    checks = []
    proved = True

    # Check 1: verified proof certificate using kdrag/Z3
    # We prove that for nonnegative integers A, M, C with A+M+C=12,
    # the target expression is always <= 112.
    A, M, C = Ints('A M C')
    expr = A*M*C + A*M + M*C + A*C
    bound_thm = ForAll(
        [A, M, C],
        Implies(
            And(A >= 0, M >= 0, C >= 0, A + M + C == 12),
            expr <= 112,
        ),
    )
    try:
        proof1 = kd.prove(bound_thm)
        checks.append({
            'name': 'upper_bound_112_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved universal upper bound with proof object: {proof1}',
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'upper_bound_112_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove upper bound: {e}',
        })

    # Check 2: verified proof certificate for attainment at (4,4,4)
    try:
        att_thm = (4*4*4 + 4*4 + 4*4 + 4*4) == 112
        proof2 = kd.prove(att_thm)
        checks.append({
            'name': 'attainment_at_444_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Concrete witness (4,4,4) yields 112; proof object: {proof2}',
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'attainment_at_444_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to verify witness value: {e}',
        })

    # Check 3: symbolic rewrite validation (not the main proof, but checked exactly)
    xA, xM, xC = symbols('A M C', integer=True, nonnegative=True)
    lhs = xA*xM*xC + xA*xM + xM*xC + xA*xC
    rhs = (xA + 1)*(xM + 1)*(xC + 1) - (xA + xM + xC) - 1
    try:
        sym_ok = expand(lhs - rhs) == 0
        checks.append({
            'name': 'symbolic_rewrite_check',
            'passed': bool(sym_ok),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'Verified exact algebraic identity: AMC+AM+MC+AC = (A+1)(M+1)(C+1) - (A+M+C) - 1.',
        })
        proved = proved and bool(sym_ok)
    except Exception as e:
        proved = False
        checks.append({
            'name': 'symbolic_rewrite_check',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Symbolic rewrite failed: {e}',
        })

    # Check 4: numerical sanity check by exhaustive enumeration of all nonnegative integer triples summing to 12
    try:
        best = None
        best_tuple = None
        for a in range(13):
            for m in range(13 - a):
                c = 12 - a - m
                val = a*m*c + a*m + m*c + a*c
                if best is None or val > best:
                    best = val
                    best_tuple = (a, m, c)
        num_pass = (best == 112 and best_tuple == (4, 4, 4))
        checks.append({
            'name': 'numerical_enumeration_sanity',
            'passed': bool(num_pass),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Exhaustive search over all nonnegative integer triples summing to 12 found maximum {best} at {best_tuple}.',
        })
        proved = proved and bool(num_pass)
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_enumeration_sanity',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical enumeration failed: {e}',
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())