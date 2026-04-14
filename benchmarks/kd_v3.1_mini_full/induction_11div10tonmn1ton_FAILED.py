import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Main formal proof: for every natural n, 11 divides 10^n - (-1)^n.
    n = Int('n')
    k = Int('k')
    expr = 10**n - (-1)**n

    try:
        # We prove the stronger statement:
        # For all n >= 0, there exists k such that 10^n - (-1)^n = 11*k.
        # Z3 can prove this by arithmetic on the base congruence 10 ≡ -1 (mod 11)
        # encoded via the divisibility witness.
        thm = kd.prove(
            ForAll([n],
                   Implies(n >= 0,
                           Exists([k], expr == 11 * k)))
        )
        checks.append({
            'name': 'divisibility_for_all_n',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm)
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'divisibility_for_all_n',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Could not construct proof certificate: {type(e).__name__}: {e}'
        })

    # Numerical sanity checks at concrete values.
    try:
        vals = []
        for nn in [0, 1, 2, 5, 10]:
            val = 10**nn - (-1)**nn
            vals.append((nn, val, val % 11))
        passed = all(rem == 0 for _, _, rem in vals)
        checks.append({
            'name': 'numerical_sanity_checks',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': '; '.join([f'n={nn}: {val} mod 11 = {rem}' for nn, val, rem in vals])
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_checks',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved and all(c['passed'] for c in checks), 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)