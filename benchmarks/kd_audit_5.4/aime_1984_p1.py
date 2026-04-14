import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified symbolic/arithmetic proof in kdrag.
    # Let s be the sum of the even-indexed terms a_2+a_4+...+a_98.
    # Since common difference is 1, each odd term satisfies a_{2k-1} = a_{2k}-1.
    # Hence total sum = (a_2-1)+a_2+...+(a_98-1)+a_98 = 2*s - 49.
    # Given total sum 137, we prove s = 93.
    try:
        s = Int('s')
        thm = ForAll([s], Implies(2 * s - 49 == 137, s == 93))
        pf = kd.prove(thm)
        checks.append({
            'name': 'kdrag_even_sum_from_total',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(pf),
        })
    except Exception as e:
        checks.append({
            'name': 'kdrag_even_sum_from_total',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}',
        })

    # Stronger verified check: if a_n = a1 + (n-1), and sum_{n=1}^{98} a_n = 137,
    # then the even-index sum is 93. Encode closed forms directly.
    try:
        a1 = Int('a1')
        even_sum = 49 * a1 + 2 * (0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                                   10 + 11 + 12 + 13 + 14 + 15 + 16 + 17 + 18 + 19 +
                                   20 + 21 + 22 + 23 + 24 + 25 + 26 + 27 + 28 + 29 +
                                   30 + 31 + 32 + 33 + 34 + 35 + 36 + 37 + 38 + 39 +
                                   40 + 41 + 42 + 43 + 44 + 45 + 46 + 47 + 48) + 49
        total_sum = 98 * a1 + (0 + 1 + 2 + 3 + 4 + 5 + 6 + 7 + 8 + 9 +
                               10 + 11 + 12 + 13 + 14 + 15 + 16 + 17 + 18 + 19 +
                               20 + 21 + 22 + 23 + 24 + 25 + 26 + 27 + 28 + 29 +
                               30 + 31 + 32 + 33 + 34 + 35 + 36 + 37 + 38 + 39 +
                               40 + 41 + 42 + 43 + 44 + 45 + 46 + 47 + 48 + 49 +
                               50 + 51 + 52 + 53 + 54 + 55 + 56 + 57 + 58 + 59 +
                               60 + 61 + 62 + 63 + 64 + 65 + 66 + 67 + 68 + 69 +
                               70 + 71 + 72 + 73 + 74 + 75 + 76 + 77 + 78 + 79 +
                               80 + 81 + 82 + 83 + 84 + 85 + 86 + 87 + 88 + 89 +
                               90 + 91 + 92 + 93 + 94 + 95 + 96 + 97)
        thm2 = ForAll([a1], Implies(total_sum == 137, even_sum == 93))
        pf2 = kd.prove(thm2)
        checks.append({
            'name': 'kdrag_closed_form_progression',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(pf2),
        })
    except Exception as e:
        checks.append({
            'name': 'kdrag_closed_form_progression',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}',
        })

    # Numerical sanity check using the deduced first term.
    try:
        # From 98*a1 + sum_{i=0}^{97} i = 137, and sum_{i=0}^{97} i = 4753.
        a1_val = (137 - 4753) / 98
        seq = [a1_val + i for i in range(98)]
        total = sum(seq)
        even_sum_val = sum(seq[i] for i in range(1, 98, 2))
        passed = abs(total - 137) < 1e-9 and abs(even_sum_val - 93) < 1e-9
        checks.append({
            'name': 'numerical_sanity_progression',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'a1={a1_val}, total={total}, even_sum={even_sum_val}',
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_progression',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'numerical check failed: {e}',
        })

    proved = all(ch['passed'] for ch in checks) and any(
        ch['passed'] and ch['proof_type'] in ('certificate', 'symbolic_zero') for ch in checks
    )
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    import json
    print(json.dumps(verify(), indent=2))