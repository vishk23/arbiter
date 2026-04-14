import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    n = Int('n')
    expr = 4 * (4**n + 5)
    stmt = ForAll([n], Implies(n >= 0, Exists([Int('k')], expr == 12 * Int('k'))))

    try:
        prf = kd.prove(stmt)
        checks.append({
            'name': 'divisibility_by_12_for_all_n',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof obtained: {prf}'
        })
    except Exception as e:
        # Fall back to a direct modular arithmetic argument checked on a few values.
        checks.append({
            'name': 'divisibility_by_12_for_all_n',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}'
        })

    # Simple arithmetic witness check: since 4^(n+1)+20 = 4*(4^n+5),
    # it is enough to show the factor is even, hence the product is divisible by 12.
    # For natural n, 4^n is even only for n>0, so instead we use direct sample checks.
    samples = [0, 1, 2, 7]
    for n0 in samples:
        val = 4**(n0 + 1) + 20
        checks.append({
            'name': f'numerical_sanity_n_equals_{n0}',
            'passed': (val % 12 == 0),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'For n={n0}, 4^(n+1)+20 = {val}, divisible by 12: {val % 12 == 0}'
        })

    return checks


if __name__ == '__main__':
    print(verify())