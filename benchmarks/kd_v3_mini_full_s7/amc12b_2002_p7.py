import kdrag as kd
from kdrag.smt import *


def _prove_consecutive_integers_solution():
    # Let the three consecutive positive integers be n-1, n, n+1.
    n = Int('n')
    premise = And(n > 0, (n - 1) * n * (n + 1) == 8 * ((n - 1) + n + (n + 1)))
    conclusion = n == 5
    thm = kd.prove(ForAll([n], Implies(premise, conclusion)))
    return thm


def _prove_sum_of_squares():
    n = Int('n')
    thm = kd.prove(ForAll([n], Implies(n == 5, (n - 1) * (n - 1) + n * n + (n + 1) * (n + 1) == 77)))
    return thm


def _numerical_sanity_check():
    n = 5
    lhs = (n - 1) * n * (n + 1)
    rhs = 8 * ((n - 1) + n + (n + 1))
    ssum = (n - 1) ** 2 + n ** 2 + (n + 1) ** 2
    passed = (lhs == rhs) and (ssum == 77)
    return {
        'name': 'numerical_sanity_check_n_equals_5',
        'passed': passed,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'n=5 gives product={lhs}, 8*sum={rhs}, sum_of_squares={ssum}',
    }


def verify():
    checks = []
    proved = True

    try:
        thm1 = _prove_consecutive_integers_solution()
        checks.append({
            'name': 'unique_middle_integer_is_5',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm1),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'unique_middle_integer_is_5',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Knuclkedragger proof failed: {e}',
        })

    try:
        thm2 = _prove_sum_of_squares()
        checks.append({
            'name': 'sum_of_squares_is_77',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm2),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sum_of_squares_is_77',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Knuckledragger proof failed: {e}',
        })

    num_check = _numerical_sanity_check()
    checks.append(num_check)
    proved = proved and all(c['passed'] for c in checks)

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)