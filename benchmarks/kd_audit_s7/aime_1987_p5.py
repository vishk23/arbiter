from sympy import *
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Main theorem: if y^2 + 3x^2 y^2 = 30x^2 + 517, then 3x^2 y^2 = 588.
    x, y = Ints('x y')
    theorem = ForAll([x, y], Implies(y*y + 3*x*x*y*y == 30*x*x + 517, 3*x*x*y*y == 588))
    try:
        pr = kd.prove(theorem)
        checks.append({
            'name': 'main_theorem_kdrag',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(pr),
        })
    except Exception as e:
        checks.append({
            'name': 'main_theorem_kdrag',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}',
        })

    # SymPy arithmetic check: from the intended solution x^2=4, y^2=49.
    try:
        lhs = (1 + 3 * Integer(4)) * Integer(49)
        rhs = 30 * Integer(4) + 517
        passed = (lhs == rhs) and (3 * Integer(4) * Integer(49) == Integer(588))
        checks.append({
            'name': 'arithmetic_certificate',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'(1+3*4)*49={lhs}, 30*4+517={rhs}, 3*4*49={3*Integer(4)*Integer(49)}',
        })
    except Exception as e:
        checks.append({
            'name': 'arithmetic_certificate',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'sympy check failed: {type(e).__name__}: {e}',
        })

    return checks