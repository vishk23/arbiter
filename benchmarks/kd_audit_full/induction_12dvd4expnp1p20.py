from kdrag.smt import *
import kdrag as kd


def _prove_main_theorem():
    n = Int('n')
    # For natural numbers n, 4^(n+1) + 20 is divisible by 12.
    # We prove the equivalent statement using modular arithmetic:
    # 4^(n+1) ≡ 4 (mod 12) for all n >= 0, hence the sum is 24 mod 12.
    return kd.prove(
        ForAll([n], Implies(n >= 0, ((4**(n + 1) + 20) % 12) == 0))
    )


def _numerical_sanity_check():
    # Concrete checks for a few values.
    vals = []
    for n in [0, 1, 2, 5, 10]:
        vals.append((4 ** (n + 1) + 20) % 12 == 0)
    return all(vals), vals


def verify():
    checks = []
    proved = True

    try:
        proof = _prove_main_theorem()
        checks.append({
            'name': 'main_theorem_divisibility',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {proof}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'main_theorem_divisibility',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {type(e).__name__}: {e}'
        })

    ok, vals = _numerical_sanity_check()
    checks.append({
        'name': 'numerical_sanity',
        'passed': ok,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Checked n in [0,1,2,5,10]; residues={vals}'
    })
    proved = proved and ok

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)