import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Main theorem: if a^2 + b^2 = 1 then ab + |a-b| <= 1.
    a, b = Reals('a b')
    main_formula = ForAll(
        [a, b],
        Implies(a * a + b * b == 1,
                a * b + If(a - b >= 0, a - b, b - a) <= 1)
    )

    try:
        proof = kd.prove(main_formula)
        checks.append({
            'name': 'main_inequality_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {proof}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'main_inequality_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {type(e).__name__}: {e}'
        })

    # Verified symbolic sanity check using SymPy algebraic simplification.
    # Let t = |a-b| >= 0, then ab = (1 - t^2)/2 under a^2+b^2=1 and
    # ab + t - 1 = -(t-1)^2/2 <= 0.
    try:
        import sympy as sp
        t = sp.symbols('t', real=True, nonnegative=True)
        expr = (1 - t**2) / 2 + t - 1
        simplified = sp.simplify(expr)
        passed = sp.factor(simplified) == -(t - 1)**2 / 2 or sp.expand(simplified + (t - 1)**2 / 2) == 0
        checks.append({
            'name': 'sympy_symbolic_rewrite',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'simplified ab+|a-b|-1 to {simplified}'
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_symbolic_rewrite',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check at a concrete point satisfying a^2+b^2=1.
    try:
        import math
        a0 = 3 / 5
        b0 = 4 / 5
        lhs = a0 * b0 + abs(a0 - b0)
        rhs = 1.0
        passed = abs(a0 * a0 + b0 * b0 - 1.0) < 1e-12 and lhs <= rhs + 1e-12
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'a={a0}, b={b0}, a^2+b^2={a0*a0+b0*b0}, ab+|a-b|={lhs}'
        })
        proved = proved and bool(passed)
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