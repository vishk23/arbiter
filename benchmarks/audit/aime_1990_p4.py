from z3 import Solver, Real, RealVal, And, Or, Not, sat, unsat


def verify():
    results = {}

    # Check 1: The transformed equation implies a = 10.
    a = Real('a')
    s1 = Solver()
    s1.set(timeout=30000)
    s1.add(a != RealVal(10))
    s1.add(RealVal(1)/a + RealVal(1)/(a - RealVal(16)) - RealVal(2)/(a - RealVal(40)) == 0)
    r1 = s1.check()
    results['check1'] = {
        'name': 'Derived substitution equation has only a = 10',
        'result': 'SAT' if r1 == sat else 'UNSAT' if r1 == unsat else 'UNKNOWN',
        'expected': 'UNSAT',
        'explanation': 'If unsat, then the transformed equation forces a = 10.',
        'passed': r1 == unsat,
    }

    # Check 2: Re-substitution yields x = 13 or x = -3, so no positive solution other than 13.
    x = Real('x')
    s2 = Solver()
    s2.set(timeout=30000)
    s2.add(x > 0)
    s2.add(x != RealVal(13))
    s2.add(x*x - RealVal(10)*x - RealVal(29) == RealVal(10))
    r2 = s2.check()
    results['check2'] = {
        'name': 'Positive solution from a = 10 is uniquely x = 13',
        'result': 'SAT' if r2 == sat else 'UNSAT' if r2 == unsat else 'UNKNOWN',
        'expected': 'UNSAT',
        'explanation': 'If unsat, then among positive x satisfying x^2 - 10x - 29 = 10, only x = 13 remains.',
        'passed': r2 == unsat,
    }

    return results


if __name__ == '__main__':
    out = verify()
    for k, v in out.items():
        print(k, v)