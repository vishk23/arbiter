import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved_all = True

    # Certified proof: 3*8 ≡ 2 (mod 11), i.e. (3*8 - 2) is divisible by 11.
    try:
        thm = kd.prove((3 * 8 - 2) % 11 == 0)
        checks.append({
            'name': 'residue_8_satisfies_congruence',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {thm}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'residue_8_satisfies_congruence',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Certified proof of the general solution: if 3n ≡ 2 (mod 11), then n ≡ 8 (mod 11).
    try:
        n = Int('n')
        uniq = kd.prove(ForAll([n], Implies((3 * n - 2) % 11 == 0, n % 11 == 8)))
        checks.append({
            'name': 'unique_solution_is_8',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {uniq}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'unique_solution_is_8',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check: compute the inverse of 3 modulo 11 and verify the residue.
    try:
        inv3 = None
        for k in range(11):
            if (3 * k) % 11 == 1:
                inv3 = k
                break
        n_val = (2 * inv3) % 11 if inv3 is not None else None
        passed = (inv3 == 4) and (n_val == 8) and ((3 * n_val - 2) % 11 == 0)
        if not passed:
            proved_all = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'inv3={inv3}, n=(2*inv3)%11={n_val}, check={(3 * n_val - 2) % 11 if n_val is not None else None}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)