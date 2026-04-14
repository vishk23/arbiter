from kdrag.smt import *
import kdrag as kd
from sympy import gcd as sympy_gcd, symbols


def verify():
    checks = []
    proved = True

    # Verified proof: any common divisor of 21n+4 and 14n+3 must divide 1.
    n, d = Ints('n d')
    gcd_thm = ForAll(
        [n, d],
        Implies(
            And(n >= 0, d > 0, (21*n + 4) % d == 0, (14*n + 3) % d == 0),
            d == 1,
        ),
    )
    try:
        proof = kd.prove(gcd_thm)
        checks.append(
            {
                'name': 'gcd_is_one_for_21n_plus_4_and_14n_plus_3',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': str(proof),
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'gcd_is_one_for_21n_plus_4_and_14n_plus_3',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Proof failed: {e}',
            }
        )

    # Numerical sanity check at a concrete value.
    try:
        n0 = 5
        num = 21 * n0 + 4
        den = 14 * n0 + 3
        g = sympy_gcd(num, den)
        checks.append(
            {
                'name': 'numerical_sanity_check_n_equals_5',
                'passed': (g == 1),
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'For n={n0}, gcd({num}, {den}) = {g}.',
            }
        )
        if g != 1:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'numerical_sanity_check_n_equals_5',
                'passed': False,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'Numerical check failed: {e}',
            }
        )

    return {'proved': proved and all(c['passed'] for c in checks), 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)