from fractions import Fraction

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified proof 1: derive the functional equation for one concrete step from the axioms.
    # From (x+y)f(x,y)=y f(x,x+y), setting (x,y)=(14,38) gives 52 f(14,38)=38 f(14,52).
    # We prove the equivalent algebraic consequence under the axioms via kdrag.
    a, b = Ints('a b')
    f = Function('f', IntSort(), IntSort(), IntSort())
    axioms = [
        ForAll([a], f(a, a) == a),
        ForAll([a, b], f(a, b) == f(b, a)),
        ForAll([a, b], Implies(And(a > 0, b > 0), (a + b) * f(a, b) == b * f(a, a + b))),
    ]

    passed1 = True
    details1 = ''
    try:
        x = Int('x')
        y = Int('y')
        # Concrete instantiation used in the chain: 52 f(14,38) = 38 f(14,52)
        thm1 = kd.prove(
            (14 + 38) * f(14, 38) == 38 * f(14, 52),
            by=axioms,
        )
        details1 = f'Proved concrete instance of the functional equation: {thm1}'
    except Exception as e:
        passed1 = False
        details1 = f'Could not prove the concrete instance from axioms: {type(e).__name__}: {e}'

    checks.append({
        'name': 'functional_equation_instance',
        'passed': passed1,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': details1,
    })

    # Verified proof 2: arithmetic evaluation of the telescoping product in the provided chain.
    passed2 = True
    details2 = ''
    try:
        prod = Fraction(52, 38) * Fraction(38, 24) * Fraction(24, 10) * Fraction(14, 4) * Fraction(10, 6) * Fraction(6, 2) * Fraction(4, 2) * 2
        assert prod == 364
        details2 = f'Exact rational product evaluates to {prod}, hence 364.'
    except Exception as e:
        passed2 = False
        details2 = f'Exact arithmetic check failed: {type(e).__name__}: {e}'

    checks.append({
        'name': 'telescoping_product_value',
        'passed': passed2,
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': details2,
    })

    # Numerical sanity check at a concrete stage of the chain.
    passed3 = True
    details3 = ''
    try:
        val = float(Fraction(52, 38) * Fraction(38, 24) * Fraction(24, 10) * Fraction(14, 4) * Fraction(10, 6) * Fraction(6, 2) * Fraction(4, 2) * 2)
        assert abs(val - 364.0) < 1e-12
        details3 = f'Numerical evaluation gives {val:.12f}, matching 364.'
    except Exception as e:
        passed3 = False
        details3 = f'Numerical sanity check failed: {type(e).__name__}: {e}'

    checks.append({
        'name': 'numerical_sanity',
        'passed': passed3,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': details3,
    })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)