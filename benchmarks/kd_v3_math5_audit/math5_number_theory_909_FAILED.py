import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof in kdrag that every valid base b is a divisor of 2010.
    # We encode the key number-theoretic characterization:
    # If 2013 ends in digit 3 in base b, then 2013 ≡ 3 (mod b), i.e. b | 2010.
    b = Int('b')
    try:
        thm1 = kd.prove(ForAll([b], Implies(And(b > 3, b > 0, 2013 % b == 3), 2010 % b == 0)))
        checks.append({
            'name': 'congruence_implies_divisibility',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved by kd.prove: {thm1}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'congruence_implies_divisibility',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}'
        })

    # Check 2: Verified symbolic count using SymPy divisor enumeration.
    try:
        divs = sp.divisors(2010)
        count = sum(1 for d in divs if d > 3)
        passed = (count == 13)
        if not passed:
            proved = False
        checks.append({
            'name': 'count_divisors_greater_than_3',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'SymPy divisors of 2010 are {divs}; count of divisors > 3 is {count}.'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'count_divisors_greater_than_3',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'SymPy check failed: {type(e).__name__}: {e}'
        })

    # Check 3: Numerical sanity checks for concrete bases.
    try:
        examples = {
            4: 2013 % 4,
            5: 2013 % 5,
            67: 2013 % 67,
            2: 2013 % 2,
        }
        passed = (examples[4] == 1 and examples[5] == 3 and examples[67] == 3 and examples[2] == 1)
        if not passed:
            proved = False
        checks.append({
            'name': 'numerical_sanity_checks',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Sample remainders: {examples}. In particular, base 5 and 67 end in digit 3, while base 4 does not.'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_checks',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical sanity check failed: {type(e).__name__}: {e}'
        })

    # Optional additional verified symbolic factorization/count explanation.
    try:
        factorization = sp.factorint(2010)
        divisor_count = 1
        for exp in factorization.values():
            divisor_count *= (exp + 1)
        passed = (factorization == {2: 1, 3: 1, 5: 1, 67: 1} and divisor_count == 16)
        if not passed:
            proved = False
        checks.append({
            'name': 'factorization_and_total_divisor_count',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'factorint(2010)={factorization}, total divisor count={divisor_count}.'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'factorization_and_total_divisor_count',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'Factorization check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())