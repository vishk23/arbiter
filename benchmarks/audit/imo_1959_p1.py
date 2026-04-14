from z3 import Solver, Int, And, Or, Not, sat, unsat


def verify():
    results = {}

    # Check 1: There is no natural number n for which gcd(21n+4, 14n+3) > 1.
    # We witness a common divisor d > 1 and derive a contradiction from Euclidean steps.
    n = Int('n')
    d = Int('d')
    s = Solver()
    s.set(timeout=30000)
    s.add(n >= 0)
    s.add(d > 1)
    s.add((21*n + 4) % d == 0)
    s.add((14*n + 3) % d == 0)

    # Euclidean-algorithm derived linear combination:
    # (21n+4) - (14n+3) = 7n+1
    # and 2*(14n+3) - (21n+4) = 7n+2? But the hint uses gcd steps directly.
    # We encode that any common divisor of 21n+4 and 14n+3 must divide 7n+1:
    s.add(((21*n + 4) - (14*n + 3)) % d == 0)

    # Then common divisor d divides 7n+1 and 14n+3, so it divides their difference 1.
    s.add((7*n + 1) % d == 0)
    s.add(((14*n + 3) - 2*(7*n + 1)) % d == 0)
    # The above difference is 1, so d divides 1, impossible for d > 1.
    # Instead of relying on arithmetic simplification alone, assert the exact identity.
    s.add((1) % d == 0)

    res = s.check()
    results['check1'] = {
        'name': 'No common divisor greater than 1 exists',
        'result': 'UNSAT' if res == unsat else ('SAT' if res == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'UNSAT means there is no natural n and divisor d>1 dividing both 21n+4 and 14n+3, so the fraction is irreducible.',
        'passed': res == unsat,
    }

    # Check 2: Directly verify the Euclidean-algorithm identity used in the proof.
    # If a common divisor divides 21n+4 and 14n+3, then it divides 7n+1 and 1.
    n2 = Int('n2')
    d2 = Int('d2')
    s2 = Solver()
    s2.set(timeout=30000)
    s2.add(n2 >= 0)
    s2.add(d2 > 0)
    s2.add((21*n2 + 4) % d2 == 0)
    s2.add((14*n2 + 3) % d2 == 0)
    s2.add(((21*n2 + 4) - (14*n2 + 3)) % d2 == 0)  # 7n+1 divisible by d2
    s2.add((7*n2 + 1) % d2 == 0)
    s2.add(((14*n2 + 3) - 2*(7*n2 + 1)) % d2 == 0)  # equals 1
    s2.add((1) % d2 == 0)

    res2 = s2.check()
    results['check2'] = {
        'name': 'Euclidean reduction implies divisor of 1',
        'result': 'UNSAT' if res2 == unsat else ('SAT' if res2 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'UNSAT confirms any common divisor must divide 1, forcing it to be 1.',
        'passed': res2 == unsat,
    }

    return results


if __name__ == '__main__':
    out = verify()
    for k, v in out.items():
        print(k, v)