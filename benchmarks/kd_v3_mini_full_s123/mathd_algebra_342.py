from fractions import Fraction

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Formalize the arithmetic-sequence equations:
    # 5a + 10d = 70 and 10a + 45d = 210.
    a, d = Reals('a d')

    eq1 = 5 * a + 10 * d == 70
    eq2 = 10 * a + 45 * d == 210
    target = a == Fraction(42, 5)

    # Verified proof: from eq1 and eq2 derive a = 42/5.
    # We ask Z3 to prove the implication directly.
    try:
        thm = kd.prove(ForAll([a, d], Implies(And(eq1, eq2), a == RealVal('42/5'))))
        checks.append({
            'name': 'deduce_first_term_from_sum_equations',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'deduce_first_term_from_sum_equations',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}',
        })

    # A second verified proof: the linear elimination step yields 5a = 42.
    try:
        thm2 = kd.prove(ForAll([a, d], Implies(And(eq1, eq2), 5 * a == 42)))
        checks.append({
            'name': 'elimination_yields_5a_equals_42',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm2),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'elimination_yields_5a_equals_42',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}',
        })

    # Numerical sanity check with the claimed value a = 42/5.
    a_val = Fraction(42, 5)
    d_val = Fraction(14, 5)
    s5 = 5 * a_val + 10 * d_val
    s10 = 10 * a_val + 45 * d_val
    num_passed = (s5 == 70) and (s10 == 210)
    checks.append({
        'name': 'numerical_sanity_check',
        'passed': num_passed,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Using a=42/5, d=14/5 gives S5={s5}, S10={s10}.',
    })
    proved = proved and num_passed

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)