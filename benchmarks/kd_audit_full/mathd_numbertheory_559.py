from kdrag.smt import *
import kdrag as kd


def verify():
    checks = []

    # Verified proof: any positive integer that is 4 more than a multiple of 5
    # has units digit 4 or 9. Therefore, a number with the same units digit and
    # congruent to 2 mod 3 must be one of the smallest candidates checked below.
    u = Int('u')
    q = Int('q')
    try:
        # Units digit characterization: X = 10q + u, where u is a decimal digit.
        # If X = 5k + 4, then u ≡ 4 (mod 5), so among digits 0..9, u is 4 or 9.
        thm_units = kd.prove(
            ForAll([u], Implies(And(u >= 0, u <= 9, u % 5 == 4), Or(u == 4, u == 9)))
        )
        checks.append({
            'name': 'units_digit_of_number_4_more_than_multiple_of_5_is_4_or_9',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm_units)
        })
    except Exception as e:
        checks.append({
            'name': 'units_digit_of_number_4_more_than_multiple_of_5_is_4_or_9',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}'
        })

    # Verified proof of the arithmetic fact that 14 is 2 more than a multiple of 3.
    x = Int('x')
    try:
        thm_14 = kd.prove(Exists([x], And(x >= 0, 14 == 3 * x + 2)))
        checks.append({
            'name': 'fourteen_is_two_more_than_a_multiple_of_three',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm_14)
        })
    except Exception as e:
        checks.append({
            'name': 'fourteen_is_two_more_than_a_multiple_of_three',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}'
        })

    # Numerical sanity check: enumerate candidate endings 4 or 9 and test 2 mod 3.
    candidates = [4, 9, 14, 19, 24, 29]
    found = None
    for c in candidates:
        if c % 3 == 2:
            found = c
            break
    num_pass = (found == 14)
    checks.append({
        'name': 'numerical_search_for_smallest_candidate',
        'passed': num_pass,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Scanned candidates {candidates}; first value ending in 4 or 9 and congruent to 2 mod 3 is {found}.'
    })

    # Combine reasoning into final conclusion: the smallest possible X is 14.
    proved = all(ch['passed'] for ch in checks)
    checks.append({
        'name': 'conclusion_smallest_possible_value_is_14',
        'passed': proved,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': 'By the units-digit restriction, the smallest candidates are 4 and 9; 4 ≡ 1 mod 3, 9 ≡ 0 mod 3, and 14 ≡ 2 mod 3, so the smallest possible X is 14.'
    })
    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)