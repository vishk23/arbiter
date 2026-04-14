import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof 1: odd square is 1 mod 8.
    a, m = Ints('a m')
    odd_sq_thm = None
    try:
        odd_sq_thm = kd.prove(
            ForAll([m], ((2 * m + 1) * (2 * m + 1) - 1) % 8 == 0)
        )
        checks.append(
            {
                'name': 'odd_square_congruence_mod_8',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': 'kd.prove certified that (2m+1)^2 ≡ 1 mod 8 for all integers m.',
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'odd_square_congruence_mod_8',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Proof failed: {e}',
            }
        )

    # Verified proof 2: if 4 | b then b^2 ≡ 0 mod 8.
    b, k = Ints('b k')
    b_sq_thm = None
    try:
        b_sq_thm = kd.prove(
            ForAll([k], ((4 * k) * (4 * k)) % 8 == 0)
        )
        checks.append(
            {
                'name': 'multiple_of_4_square_congruence_mod_8',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': 'kd.prove certified that (4k)^2 ≡ 0 mod 8 for all integers k.',
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'multiple_of_4_square_congruence_mod_8',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Proof failed: {e}',
            }
        )

    # Main theorem: odd a and 4 | b implies a^2 + b^2 ≡ 1 mod 8.
    try:
        a, m, k = Ints('a m k')
        main_thm = kd.prove(
            ForAll(
                [m, k],
                (((2 * m + 1) * (2 * m + 1) + (4 * k) * (4 * k) - 1) % 8) == 0,
            )
        )
        checks.append(
            {
                'name': 'main_congruence_theorem',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': 'kd.prove certified the combined congruence (2m+1)^2 + (4k)^2 ≡ 1 mod 8.',
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'main_congruence_theorem',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Proof failed: {e}',
            }
        )

    # Numerical sanity check.
    try:
        a0 = 7  # odd
        b0 = 12  # divisible by 4
        val = (a0 * a0 + b0 * b0) % 8
        passed = (val == 1)
        checks.append(
            {
                'name': 'numerical_sanity_check',
                'passed': passed,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'For a={a0}, b={b0}, (a^2+b^2) mod 8 = {val}.',
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'numerical_sanity_check',
                'passed': False,
                'backend': 'numerical',
                'proof_type': 'numerical',
                'details': f'Numerical check failed: {e}',
            }
        )

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())