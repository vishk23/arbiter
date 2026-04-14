import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    n = Int('n')
    f = Function('f', IntSort(), IntSort())

    # Define the recurrence exactly as given.
    rec = kd.axiom(ForAll([n],
        If(n >= 1000,
           f(n) == n - 3,
           f(n) == f(f(n + 5)))))

    # A direct consequence of the recurrence at n = 999:
    # f(999) = f(f(1004)) = f(1001) = 998.
    # This implies f(994) = f(f(999)) = f(998), etc., and the standard backward
    # chase for this problem yields f(84) = 997.
    # We verify the concrete target by asking the prover to establish it from
    # the recurrence encoded above.
    try:
        p = kd.prove(f(84) == 997, by=[rec])
        checks.append({
            'name': 'prove_f84_equals_997',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'proof',
            'details': str(p)
        })
    except Exception as e:
        checks.append({
            'name': 'prove_f84_equals_997',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'proof',
            'details': str(e)
        })

    return checks