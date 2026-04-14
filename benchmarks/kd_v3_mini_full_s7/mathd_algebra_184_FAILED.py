import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified symbolic proof with kdrag/Z3:
    # From geometric sequence relations:
    #   a^2 = 6*b
    #   a^2 = 54/b
    # With b > 0, derive b = 3 and then a^2 = 18.
    a, b = Reals('a b')

    # Check 1: prove the key algebraic consequence b = 3 from the two geometric relations.
    try:
        thm_b = kd.prove(
            ForAll([a, b],
                   Implies(
                       And(a > 0, b > 0, a*a == 6*b, a*a == 54/b),
                       b == 3
                   )),
        )
        checks.append({
            'name': 'derive_b_equals_3',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm_b)
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'derive_b_equals_3',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    # Check 2: prove that if b = 3 and a^2 = 6b then a = 3*sqrt(2) for positive a.
    try:
        thm_a = kd.prove(
            ForAll([a],
                   Implies(
                       And(a > 0, a*a == 18),
                       a == 3*sp.sqrt(2)
                   )),
        )
        checks.append({
            'name': 'derive_a_equals_3_sqrt_2',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm_a)
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'derive_a_equals_3_sqrt_2',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    # Check 3: numerical sanity check at the concrete solution.
    try:
        a_val = 3 * sp.sqrt(2)
        b_val = sp.Integer(3)
        lhs1 = sp.simplify(a_val**2)
        rhs1 = sp.simplify(6*b_val)
        rhs2 = sp.simplify(54/b_val)
        passed = (lhs1 == rhs1 == rhs2 == 18)
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'a=3*sqrt(2), b=3 gives a^2={lhs1}, 6b={rhs1}, 54/b={rhs2}'
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'numerical check failed: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())