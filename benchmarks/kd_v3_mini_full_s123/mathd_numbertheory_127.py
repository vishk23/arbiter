import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: prove the remainder is 3 using modular arithmetic in Z3.
    # We encode the statement as an existential witness for the quotient:
    #   sum = 7*q + 3
    # where sum = 1 + 2 + ... + 2^100.
    # Rather than building the full power tower in Z3, we use the exact closed form
    # sum = 2^101 - 1 and then prove the modular fact 2^101 ≡ 4 (mod 7) using periodicity.
    # Since 2^3 ≡ 1 (mod 7), 2^101 = 2^(3*33+2) ≡ 2^2 = 4 (mod 7), so sum ≡ 3.

    try:
        q = Int('q')
        # Direct arithmetic certificate that the claimed remainder is 3.
        # This is equivalent to proving the divisibility statement:
        #   (2**101 - 1) - 3 is divisible by 7
        # i.e. 2**101 - 4 is divisible by 7.
        # Z3 can verify the concrete integer arithmetic once we supply the exact value.
        thm = kd.prove(Exists([q], 2**101 - 4 == 7 * q))
        checks.append({
            'name': 'modular_divisibility_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove certified that 2^101 - 4 is divisible by 7: {thm}',
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'modular_divisibility_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to certify divisibility in kdrag: {e}',
        })

    # Numerical sanity check at the concrete problem size.
    try:
        total = sum(2**k for k in range(101))
        rem = total % 7
        ok = (rem == 3)
        checks.append({
            'name': 'numerical_remainder_check',
            'passed': ok,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'sum(2^k, k=0..100) % 7 = {rem}',
        })
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_remainder_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical computation failed: {e}',
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)