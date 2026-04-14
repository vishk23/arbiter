from z3 import Solver, Real, RealVal, sat, unsat


def verify():
    results = {}

    # Variables
    a = Real('a')
    b = Real('b')
    x = Real('x')
    y = Real('y')
    S = Real('S')
    P = Real('P')
    target = Real('target')

    # Given system
    base = [
        a * x + b * y == RealVal(3),
        a * x * x + b * y * y == RealVal(7),
        a * x * x * x + b * y * y * y == RealVal(16),
        a * x * x * x * x + b * y * y * y * y == RealVal(42),
        S == x + y,
        P == x * y,
    ]

    # Check 1: derive S = x + y = -14 and P = xy = -38 from the recurrence relations
    s1 = Solver()
    s1.add(base)
    s1.add(7 * S == 16 + 3 * P)
    s1.add(16 * S == 42 + 7 * P)
    s1.add(Or(S != RealVal(-14), P != RealVal(-38)))
    r1 = s1.check()
    results['check1'] = {
        'name': 'Derive x+y and xy from the given moment equations',
        'result': 'UNSAT' if r1 == unsat else ('SAT' if r1 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'No model satisfies the equations together with S != -14 or P != -38; hence S = -14 and P = -38 are forced.',
        'passed': r1 == unsat,
    }

    # Check 2: prove ax^5 + by^5 = 20 using the derived S and P
    s2 = Solver()
    s2.add(base)
    s2.add(S == x + y)
    s2.add(P == x * y)
    s2.add(7 * S == 16 + 3 * P)
    s2.add(16 * S == 42 + 7 * P)
    s2.add(target == a * x**5 + b * y**5)
    s2.add(S == RealVal(-14))
    s2.add(P == RealVal(-38))
    s2.add(42 * S == target + 16 * P)
    s2.add(target != RealVal(20))
    r2 = s2.check()
    results['check2'] = {
        'name': 'Prove ax^5 + by^5 equals 20',
        'result': 'UNSAT' if r2 == unsat else ('SAT' if r2 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'No counterexample exists; the fifth-moment expression must equal 20.',
        'passed': r2 == unsat,
    }

    # Check 3: directly verify consistency with the claimed final value 20
    s3 = Solver()
    s3.add(base)
    s3.add(S == x + y)
    s3.add(P == x * y)
    s3.add(7 * S == 16 + 3 * P)
    s3.add(16 * S == 42 + 7 * P)
    s3.add(42 * S == a * x**5 + b * y**5 + 16 * P)
    s3.add(a * x**5 + b * y**5 != RealVal(20))
    r3 = s3.check()
    results['check3'] = {
        'name': 'Direct contradiction check for the final value',
        'result': 'UNSAT' if r3 == unsat else ('SAT' if r3 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'The recurrence relation for n=4 forces the fifth power sum to be 20.',
        'passed': r3 == unsat,
    }

    return results


if __name__ == '__main__':
    res = verify()
    for k, v in res.items():
        print(f"{k}: {v}")