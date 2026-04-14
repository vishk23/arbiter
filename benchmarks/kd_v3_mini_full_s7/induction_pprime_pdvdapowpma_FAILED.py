import kdrag as kd
from kdrag.smt import *
from sympy import isprime


def verify():
    checks = []
    proved = True

    # Verified proof: for all integers a, if p is prime then p divides a^p - a.
    # We encode the divisibility statement as an existence of an integer quotient.
    p, a, q = Ints('p a q')
    statement = ForAll(
        [p, a],
        Implies(
            And(p > 1, isprime(2) == True),
            Exists([q], a**p - a == p * q)
        )
    )

    # The above is not the intended encoding of primality and is not a valid theorem
    # because Z3 cannot reason about Python's sympy.isprime inside the logic.
    # Instead, we provide a concrete verified sanity proof that captures the core algebraic
    # divisibility mechanism on a representative prime and a general numerical check below.
    
    # Certificate-backed proof for a concrete prime instance: p = 5, a = 12.
    # 12^5 - 12 = 2488200 = 5 * 497640.
    q0 = Int('q0')
    concrete = kd.prove(Exists([q0], 12**5 - 12 == 5 * q0))
    checks.append({
        'name': 'concrete_prime_instance_certificate',
        'passed': True,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': f'kd.prove returned proof: {concrete}'
    })

    # Symbolic statement using Fermat's little theorem cannot be fully certified here
    # without a formal primality theory and modular exponentiation library in kdrag.
    # Therefore we report it as not fully proved in this module.
    checks.append({
        'name': 'general_fermat_little_theorem_statement',
        'passed': False,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': 'General proof over arbitrary prime p was not encoded in a theorem-prover-complete way here; a fully formal primality-and-modular-arithmetic development is unavailable in this standalone module.'
    })
    proved = False

    # Numerical sanity check: verify a few concrete values.
    numeric_cases = [(2, 3), (3, 4), (5, 7), (7, 10)]
    num_pass = True
    details = []
    for pp, aa in numeric_cases:
        val = aa**pp - aa
        ok = (val % pp == 0)
        num_pass = num_pass and ok
        details.append(f'p={pp}, a={aa}: (a^p-a) mod p = {val % pp}')
    checks.append({
        'name': 'numerical_sanity_checks',
        'passed': num_pass,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': '; '.join(details)
    })
    proved = proved and num_pass

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)