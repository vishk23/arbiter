import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: verified proof certificate in kdrag for the key arithmetic claim.
    # If a and b are positive integers with ab = 2005 and neither is 1,
    # then the factor pair must be 5 and 401, so their sum is 406.
    a, b = Ints('a b')
    thm = ForAll(
        [a, b],
        Implies(
            And(a > 0, b > 0, a * b == 2005, a != 1, b != 1),
            a + b == 406,
        ),
    )
    try:
        proof = kd.prove(thm)
        checks.append(
            {
                'name': 'factor_pair_sum_is_406',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove returned certificate: {proof}',
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'factor_pair_sum_is_406',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kdrag proof failed: {type(e).__name__}: {e}',
            }
        )

    # Check 2: symbolic verification that 401 is prime.
    # We use SymPy's exact primality test as supporting evidence.
    is_401_prime = sp.isprime(401)
    passed_prime = bool(is_401_prime)
    if not passed_prime:
        proved = False
    checks.append(
        {
            'name': '401_is_prime',
            'passed': passed_prime,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'SymPy exact primality test confirms 401 is prime.' if passed_prime else 'SymPy failed to certify 401 as prime.',
        }
    )

    # Check 3: numerical sanity check on the concrete factor pair.
    concrete_ok = (5 * 401 == 2005) and (5 + 401 == 406)
    if not concrete_ok:
        proved = False
    checks.append(
        {
            'name': 'concrete_factor_pair_sanity',
            'passed': concrete_ok,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': 'Verified numerically that 5*401 = 2005 and 5+401 = 406.',
        }
    )

    return {'proved': proved and all(c['passed'] for c in checks), 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)