from fractions import Fraction
import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # ------------------------------------------------------------
    # Check 1: Verified symbolic proof in kdrag using rational logs
    # ------------------------------------------------------------
    # Let a = ln(w), b = ln(x), c = ln(y), d = ln(z).
    # Then a/b = 24, a/c = 40, a/(b+c+d) = 12.
    # Solve algebraically to get d = a/60, hence a/d = 60.
    
    a, b, c, d = Reals('a b c d')

    # Use rational arithmetic on the relations derived from logs.
    # b = a/24, c = a/40, and b + c + d = a/12.
    thm = None
    try:
        thm = kd.prove(
            ForAll([a],
                   Implies(a > 0,
                           Exists([b, c, d],
                                  And(b == a / 24,
                                      c == a / 40,
                                      b + c + d == a / 12,
                                      a / d == 60))))
        )
        checks.append({
            'name': 'symbolic_log_ratio_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'symbolic_log_ratio_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}'
        })

    # ------------------------------------------------------------
    # Check 2: SymPy exact symbolic computation
    # ------------------------------------------------------------
    try:
        a = sp.symbols('a', positive=True)
        b = a / 24
        c = a / 40
        d = sp.simplify(a / 12 - b - c)
        ans = sp.simplify(a / d)
        passed = (ans == 60)
        if not passed:
            proved = False
        checks.append({
            'name': 'sympy_exact_solution',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Computed a/d = {ans}; expected 60.'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_exact_solution',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy computation failed: {type(e).__name__}: {e}'
        })

    # ------------------------------------------------------------
    # Check 3: Numerical sanity check with concrete values
    # Choose a convenient positive value for a = ln(w).
    # Let a = 120, then b = 5, c = 3, d = 2, and a/d = 60.
    # This matches the hint's scaling by 120.
    # ------------------------------------------------------------
    try:
        aval = 120.0
        bval = aval / 24.0
        cval = aval / 40.0
        dval = aval / 12.0 - bval - cval
        numeric_ans = aval / dval
        passed = abs(numeric_ans - 60.0) < 1e-12 and abs(bval + cval + dval - aval / 12.0) < 1e-12
        if not passed:
            proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'With a=120: b={bval}, c={cval}, d={dval}, a/d={numeric_ans}.'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)