import kdrag as kd
from kdrag.smt import *
from kdrag.kernel import LemmaError
from sympy import Symbol, minimal_polynomial, Rational


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof that a number 4 more than a multiple of 5
    # has units digit 4 or 9. We encode this as the modular characterization:
    # n = 5q + 4 => n mod 10 is 4 or 9.
    n, q, r = Ints('n q r')
    thm1 = None
    try:
        thm1 = kd.prove(
            ForAll([q], Or((5 * q + 4) % 10 == 4, (5 * q + 4) % 10 == 9))
        )
        checks.append({
            'name': 'units_digit_of_4_more_than_multiple_of_5_is_4_or_9',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm1)
        })
    except LemmaError as e:
        proved = False
        checks.append({
            'name': 'units_digit_of_4_more_than_multiple_of_5_is_4_or_9',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    # Check 2: Verified proof that 14 is 2 more than a multiple of 3.
    try:
        thm2 = kd.prove(Exists([q], 14 == 3 * q + 2))
        checks.append({
            'name': 'fourteen_is_two_more_than_multiple_of_three',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm2)
        })
    except LemmaError as e:
        proved = False
        checks.append({
            'name': 'fourteen_is_two_more_than_multiple_of_three',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    # Check 3: Verified proof of minimality among positive integers with
    # n % 3 == 2 and n % 10 == 4; show every such positive n is at least 14.
    x = Int('x')
    try:
        thm3 = kd.prove(
            ForAll([x], Implies(And(x > 0, x % 3 == 2, x % 10 == 4), x >= 14))
        )
        checks.append({
            'name': 'smallest_positive_integer_ending_in_4_and_congruent_to_2_mod_3_is_at_least_14',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm3)
        })
    except LemmaError as e:
        proved = False
        checks.append({
            'name': 'smallest_positive_integer_ending_in_4_and_congruent_to_2_mod_3_is_at_least_14',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    # Check 4: Numerical sanity check by brute force over a finite range.
    candidates = [m for m in range(1, 100) if m % 3 == 2 and m % 10 == 4]
    numerical_ok = (min(candidates) == 14 and 14 in candidates)
    checks.append({
        'name': 'numerical_sanity_smallest_candidate_is_14',
        'passed': numerical_ok,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Candidates under 100: {candidates[:10]}...; minimum={min(candidates) if candidates else None}'
    })
    proved = proved and numerical_ok

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())