import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Prove the contrapositive: if n is composite, then 2^n - 1 is composite.
    # Let n = a*b with a,b >= 2. Then
    #   2^(ab) - 1 = (2^a - 1) * (1 + 2^a + ... + 2^{a(b-1)}),
    # so 2^a - 1 is a nontrivial factor of 2^n - 1.
    a, b = Ints('a b')

    factor_divides = ForAll(
        [a, b],
        Implies(
            And(a >= 2, b >= 2),
            Exists(
                [k],
                (2 ** (a * b) - 1) == (2 ** a - 1) * k
            )
        )
    )

    nontrivial_factor = ForAll(
        [a],
        Implies(a >= 2, And(2 ** a - 1 >= 3, 2 ** a - 1 < 2 ** a))
    )

    try:
        pf1 = kd.prove(factor_divides)
        checks.append({
            'name': 'mersenne_divisibility_for_composite_exponent',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Certified by kd.prove: {pf1}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'mersenne_divisibility_for_composite_exponent',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}'
        })

    try:
        pf2 = kd.prove(nontrivial_factor)
        checks.append({
            'name': 'nontrivial_mersenne_factor',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Certified by kd.prove: {pf2}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'nontrivial_mersenne_factor',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}'
        })

    # Final theorem statement encoded as a check; if n is prime under the
    # assumption that 2^n - 1 is prime, then every composite n would contradict
    # the above divisibility property.
    n = Int('n')
    theorem = ForAll(
        [n],
        Implies(
            And(n > 0, IsPrime(2 ** n - 1)),
            IsPrime(n)
        )
    )

    try:
        pf3 = kd.prove(theorem)
        checks.append({
            'name': 'mersenne_prime_exponent_theorem',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Certified by kd.prove: {pf3}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'mersenne_prime_exponent_theorem',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}