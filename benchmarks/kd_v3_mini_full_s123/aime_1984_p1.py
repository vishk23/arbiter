import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Formalize the arithmetic progression: a_n = a1 + (n-1) since common difference is 1.
    # From sum_{n=1}^{98} a_n = 137, we derive:
    #   98*a1 + (0+1+...+97) = 137
    #   98*a1 + 4753 = 137
    # Then the even-indexed sum is:
    #   a2 + a4 + ... + a98 = sum_{m=1}^{49} (a1 + (2m-1))
    #                        = 49*a1 + (1+3+...+97)
    #                        = 49*a1 + 2401
    # Substituting the first-term equation gives 93.

    a1 = Real('a1')

    try:
        thm = kd.prove(
            ForAll([a1], Implies(98 * a1 + 4753 == 137, 49 * a1 + 2401 == 93))
        )
        checks.append({
            'name': 'arithmetic_progression_even_sum',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'arithmetic_progression_even_sum',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}',
        })

    try:
        thm2 = kd.prove(
            ForAll([a1], Implies(98 * a1 + 4753 == 137, a1 == RealVal(-2308) / RealVal(49)))
        )
        checks.append({
            'name': 'derive_first_term',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm2),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'derive_first_term',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}',
        })

    # Numerical sanity check with a concrete instance satisfying the total sum.
    # If a1 = -2308/49, then 98*a1 + 4753 = 137 and even sum is 93.
    try:
        a1_num = -2308 / 49
        total = 98 * a1_num + 4753
        even_sum = 49 * a1_num + 2401
        ok = abs(total - 137) < 1e-12 and abs(even_sum - 93) < 1e-12
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': bool(ok),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'a1={a1_num}, total={total}, even_sum={even_sum}',
        })
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}',
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)