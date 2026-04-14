import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof via kdrag (certificate-producing)
    # We prove the algebraic identity for all nonzero x.
    x = Real('x')
    expr = (12 / (x * x)) * ((x**4) / (14 * x)) * (35 / (3 * x))
    try:
        thm = kd.prove(ForAll([x], Implies(x != 0, expr == 10)))
        checks.append({
            'name': 'algebraic_simplification_identity',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'algebraic_simplification_identity',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Check 2: SymPy exact symbolic simplification sanity check
    try:
        xs = symbols('x', nonzero=True)
        sexpr = 12/(xs*xs) * (xs**4)/(14*xs) * 35/(3*xs)
        sres = simplify(sexpr)
        passed = (sres == 10)
        if not passed:
            proved = False
        checks.append({
            'name': 'sympy_symbolic_simplification',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'simplify(...) returned {sres}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_symbolic_simplification',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy check failed: {type(e).__name__}: {e}'
        })

    # Check 3: Numerical sanity check at a concrete nonzero value
    try:
        val = (12 / (2 * 2)) * ((2**4) / (14 * 2)) * (35 / (3 * 2))
        passed = abs(val - 10) < 1e-12
        if not passed:
            proved = False
        checks.append({
            'name': 'numerical_sanity_at_x_equals_2',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'value at x=2 is {val}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_at_x_equals_2',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    import pprint
    pprint.pp(verify())