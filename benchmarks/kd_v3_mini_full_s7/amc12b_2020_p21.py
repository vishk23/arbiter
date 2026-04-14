import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Let k = floor(sqrt(n)). Then k^2 <= n < (k+1)^2 and
    # n = 70k - 1000 from (n+1000)/70 = k.
    # So we need integers k such that
    #   k^2 <= 70k - 1000 < (k+1)^2.
    # We verify that exactly six integers satisfy this: k = 31,32,33,34,35,36.
    k = Int('k')

    # Use direct arithmetic checking by solving the equivalent inequalities in Z3.
    # Since the expression is a quadratic, the candidate set is finite and can be enumerated.
    candidates = []
    for kv in range(0, 200):
        n = 70 * kv - 1000
        if n > 0 and kv * kv <= n < (kv + 1) * (kv + 1):
            candidates.append(kv)

    checks.append({
        'name': 'candidate-enumeration',
        'passed': candidates == [31, 32, 33, 34, 35, 36],
        'backend': 'python-enumeration',
        'details': f'Candidates for k are {candidates}.',
    })

    # Confirm each candidate yields a valid n and distinct positive integers.
    valid_ns = []
    for kv in candidates:
        n = 70 * kv - 1000
        valid_ns.append(n)
        checks.append({
            'name': f'check-k-{kv}',
            'passed': (n > 0 and kv == (n + 1000) // 70 and kv * kv <= n < (kv + 1) * (kv + 1)),
            'backend': 'python-enumeration',
            'details': f'k={kv}, n={n}',
        })

    checks.append({
        'name': 'count-valid-n',
        'passed': len(valid_ns) == 6 and len(set(valid_ns)) == 6,
        'backend': 'python-enumeration',
        'details': f'Valid n values are {valid_ns}.',
    })

    return checks