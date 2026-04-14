from sympy import Integer

try:
    import kdrag as kd
    from kdrag.smt import Int, ForAll, Implies, And, Not
except Exception:
    kd = None


def verify():
    checks = []
    proved_all = True

    # Verified proof: 5^100 ends with 625, hence digit sum is 13.
    if kd is not None:
        try:
            n = Int('n')
            # For n >= 3, powers of 5 modulo 1000 alternate between 125 and 625.
            # In particular, 5^100 mod 1000 = 625 because 100 is even and >= 3.
            thm = kd.prove((5**100) % 1000 == 625)
            checks.append({
                'name': 'final_three_digits_of_5_pow_100',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': str(thm)
            })
        except Exception as e:
            proved_all = False
            checks.append({
                'name': 'final_three_digits_of_5_pow_100',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Could not verify 5^100 mod 1000 = 625: {e}'
            })
    else:
        proved_all = False
        checks.append({
            'name': 'final_three_digits_of_5_pow_100',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kdrag unavailable in this environment.'
        })

    # Numerical sanity checks
    v3 = int(5**3)
    v4 = int(5**4)
    v100_mod = int(pow(5, 100, 1000))
    checks.append({
        'name': 'sanity_cycle_5_cubed',
        'passed': (v3 % 1000 == 125),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'5^3 = {v3}, last three digits = {v3 % 1000}'
    })
    checks.append({
        'name': 'sanity_cycle_5_fourth',
        'passed': (v4 % 1000 == 625),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'5^4 = {v4}, last three digits = {v4 % 1000}'
    })
    checks.append({
        'name': 'sanity_5_pow_100_last_three_digits',
        'passed': (v100_mod == 625),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'pow(5, 100, 1000) = {v100_mod}, digit sum = {sum(int(d) for d in str(v100_mod).zfill(3))}'
    })

    # Final arithmetic verification for the asked sum.
    digit_sum = sum(int(d) for d in str(v100_mod).zfill(3))
    checks.append({
        'name': 'digit_sum_is_13',
        'passed': (digit_sum == 13),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Last three digits {v100_mod} have digit sum {digit_sum}'
    })

    proved_all = proved_all and all(ch['passed'] for ch in checks)
    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)