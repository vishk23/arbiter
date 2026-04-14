import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify


def verify():
    checks = []
    proved = True

    # Verified proof: encode f(1) = 5*1 + 4 = 9 in Z3/kdrag.
    try:
        x = Int('x')
        thm = kd.prove(5 * 1 + 4 == 9)
        checks.append({
            'name': 'f(1) equals 9 via kdrag proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved arithmetic equality with certificate: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'f(1) equals 9 via kdrag proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Symbolic computation check with SymPy (not the main proof certificate, but exact arithmetic).
    try:
        x = symbols('x')
        f = 5 * x + 4
        f1 = f.subs(x, 1)
        passed = simplify(f1 - 9) == 0
        checks.append({
            'name': 'SymPy substitution yields 9',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'f(1) simplified to {f1}'
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            'name': 'SymPy substitution yields 9',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'SymPy check failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check at the concrete value x=1.
    try:
        val = 5 * 1 + 4
        passed = (val == 9)
        checks.append({
            'name': 'Numerical sanity check at x=1',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Computed 5*1+4 = {val}'
        })
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append({
            'name': 'Numerical sanity check at x=1',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)