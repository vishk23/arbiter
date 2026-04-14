import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # The target statement:
    # S = (n+4) + (n+6) + (n+8) = 3n + 18.
    # If n is a multiple of 3, then n % 3 == 0, so S is a multiple of 9.
    n = Int('n')
    S = (n + 4) + (n + 6) + (n + 8)

    # Certified proof: direct divisibility claim.
    try:
        thm = kd.prove(ForAll([n], Implies(n % 3 == 0, S % 9 == 0)))
        checks.append({
            'name': 'direct_divisibility_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved by kdrag: {thm}',
        })
    except Exception as e:
        checks.append({
            'name': 'direct_divisibility_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}',
        })

    # Certified proof via explicit substitution n = 3k.
    k = Int('k')
    S_sub = (3 * k + 4) + (3 * k + 6) + (3 * k + 8)
    try:
        thm2 = kd.prove(ForAll([k], S_sub % 9 == 0))
        checks.append({
            'name': 'substitution_divisibility_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proved by kdrag: {thm2}',
        })
    except Exception as e:
        checks.append({
            'name': 'substitution_divisibility_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}',
        })

    # Numerical sanity check at a concrete multiple of 3.
    n0 = 12
    S0 = (n0 + 4) + (n0 + 6) + (n0 + 8)
    checks.append({
        'name': 'numerical_sanity_check',
        'passed': (S0 % 9 == 0),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'For n={n0}, S={S0}, S mod 9 = {S0 % 9}.',
    })

    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)