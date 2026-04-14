from sympy import symbols, Integer
import kdrag as kd
from kdrag.smt import Ints, Int, And, ForAll, Implies


def verify():
    checks = []

    # Check 1: verified symbolic proof with kdrag that the objective is at most 112
    # for all nonnegative integers A, M, C with A+M+C=12.
    try:
        A, M, C = Ints('A M C')
        expr = A*M*C + A*M + M*C + A*C
        thm = kd.prove(
            ForAll([A, M, C],
                   Implies(And(A >= 0, M >= 0, C >= 0, A + M + C == 12), expr <= 112))
        )
        checks.append({
            'name': 'kdrag_upper_bound_112',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm)
        })
    except Exception as e:
        checks.append({
            'name': 'kdrag_upper_bound_112',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}'
        })

    # Check 2: verified symbolic proof that the bound is attained at (4,4,4).
    try:
        A, M, C = Ints('A M C')
        expr = A*M*C + A*M + M*C + A*C
        thm2 = kd.prove(expr == 112, by=[] if False else None)
        # The above is intentionally not used as a proof route; we replace it below with a concrete check.
        # If kd.prove above unexpectedly succeeds, we still require the concrete instance below.
        passed = False
        details = 'Unexpected direct proof attempt; not relied upon.'
    except Exception:
        # Concrete certified arithmetic check via kdrag on the specific instance.
        try:
            A, M, C = Ints('A M C')
            inst = kd.prove((4*4*4 + 4*4 + 4*4 + 4*4) == 112)
            checks.append({
                'name': 'attained_at_444',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': str(inst)
            })
        except Exception as e:
            checks.append({
                'name': 'attained_at_444',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Concrete evaluation proof failed: {type(e).__name__}: {e}'
            })

    # Check 3: numerical/brute-force sanity check over all integer triples.
    try:
        mx = -1
        arg = None
        for a in range(13):
            for m in range(13 - a):
                c = 12 - a - m
                val = a*m*c + a*m + m*c + a*c
                if val > mx:
                    mx = val
                    arg = (a, m, c)
        passed = (mx == 112 and arg == (4, 4, 4))
        checks.append({
            'name': 'bruteforce_sanity',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'max={mx}, arg={arg}'
        })
    except Exception as e:
        checks.append({
            'name': 'bruteforce_sanity',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Bruteforce check failed: {type(e).__name__}: {e}'
        })

    proved = all(ch['passed'] for ch in checks) and any(ch['backend'] == 'kdrag' and ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)