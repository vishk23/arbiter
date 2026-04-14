from fractions import Fraction

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And

from sympy import Rational


def _numerical_sanity():
    a = Rational(2)
    b = Rational(2, 3)
    eq1 = a**2 * b**3 == Rational(32, 27)
    eq2 = a / (b**3) == Rational(27, 4)
    return bool(eq1 and eq2 and (a + b == Rational(8, 3)))


def verify():
    checks = []
    proved = True

    # Verified proof: encode the algebraic constraints and conclusion in Z3.
    a = Real('a')
    b = Real('b')
    thm = ForAll(
        [a, b],
        Implies(
            And(a * a * b * b * b == kd.smt.RealVal(32) / kd.smt.RealVal(27),
                a / (b * b * b) == kd.smt.RealVal(27) / kd.smt.RealVal(4)),
            a + b == kd.smt.RealVal(8) / kd.smt.RealVal(3),
        ),
    )
    try:
        prf = kd.prove(thm)
        checks.append(
            {
                'name': 'algebraic_deduction_of_a_plus_b',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove succeeded: {prf}',
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'algebraic_deduction_of_a_plus_b',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove failed: {type(e).__name__}: {e}',
            }
        )

    # Symbolic consistency check using exact rational arithmetic.
    try:
        a_val = Rational(2)
        b_val = Rational(2, 3)
        lhs1 = a_val**2 * b_val**3
        lhs2 = a_val / (b_val**3)
        concl = a_val + b_val
        ok = (lhs1 == Rational(32, 27)) and (lhs2 == Rational(27, 4)) and (concl == Rational(8, 3))
        checks.append(
            {
                'name': 'exact_rational_substitution',
                'passed': bool(ok),
                'backend': 'sympy',
                'proof_type': 'numerical',
                'details': f'a=2, b=2/3 gives eq1={lhs1}, eq2={lhs2}, sum={concl}',
            }
        )
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'exact_rational_substitution',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'numerical',
                'details': f'Unexpected error: {type(e).__name__}: {e}',
            }
        )

    # Additional numerical sanity check.
    num_ok = _numerical_sanity()
    checks.append(
        {
            'name': 'numerical_sanity_check',
            'passed': bool(num_ok),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': 'Verified with exact rational arithmetic on the candidate solution a=2, b=2/3.',
        }
    )
    if not num_ok:
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)