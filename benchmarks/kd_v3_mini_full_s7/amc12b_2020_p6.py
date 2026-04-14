import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, Eq, factor, simplify, factorial


def verify():
    checks = []
    proved = True

    # ------------------------------------------------------------------
    # Check 1: Verified proof in kdrag/Z3 that the expression simplifies
    # to (n+1)^2 for all integers n >= 0 (hence for n >= 9).
    # We prove the algebraic identity after rewriting factorial terms.
    # ------------------------------------------------------------------
    n = Int('n')
    expr = (((n + 2) * (n + 1) - (n + 1)))
    target = (n + 1) * (n + 1)

    try:
        thm = kd.prove(ForAll([n], expr == target))
        checks.append({
            'name': 'algebraic_identity_to_square',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned proof: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'algebraic_identity_to_square',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}'
        })

    # ------------------------------------------------------------------
    # Check 2: Symbolic verification with SymPy that the simplified form is
    # exactly (n+1)^2.
    # ------------------------------------------------------------------
    ns = Symbol('n', integer=True, positive=True)
    sym_expr = ((factorial(ns + 2) - factorial(ns + 1)) / factorial(ns)).simplify()
    sym_target = (ns + 1)**2
    try:
        passed = simplify(sym_expr - sym_target) == 0
        checks.append({
            'name': 'sympy_simplification_matches_square',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'simplified expression: {sym_expr}, target: {sym_target}'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_simplification_matches_square',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy check failed: {type(e).__name__}: {e}'
        })

    # ------------------------------------------------------------------
    # Check 3: Numerical sanity check at a concrete value n = 9.
    # ------------------------------------------------------------------
    try:
        n0 = 9
        val = ((factorial(n0 + 2) - factorial(n0 + 1)) // factorial(n0))
        expected = (n0 + 1)**2
        passed = (val == expected)
        checks.append({
            'name': 'numerical_sanity_at_n_9',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'value={val}, expected={expected}'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_at_n_9',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    # ------------------------------------------------------------------
    # Final conclusion: for all n >= 9, the value is (n+1)^2, hence a
    # perfect square.
    # ------------------------------------------------------------------
    checks.append({
        'name': 'final_conclusion_perfect_square',
        'passed': proved,
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': 'The expression equals (n+1)^2 for all integers n, so for n >= 9 it is always a perfect square.'
    })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)