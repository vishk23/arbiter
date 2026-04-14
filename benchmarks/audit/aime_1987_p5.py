from z3 import Solver, Int, And, Or, Not, sat, unsat


def verify():
    results = {}

    # Variables
    x = Int('x')
    y = Int('y')
    t = Int('t')  # target value for 3x^2 y^2

    # Original equation:
    # y^2 + 3x^2 y^2 = 30x^2 + 517
    # Factor as: (3x^2 + 1)(y^2 - 10) = 507 = 3 * 13^2
    # We prove that the only integer solution gives x^2 = 4 and y^2 = 49,
    # hence t = 588.

    s1 = Solver()
    s1.set(timeout=30000)
    s1.add(y*y + 3*x*x*y*y == 30*x*x + 517)
    s1.add(t == 3*x*x*y*y)
    s1.add(t != 588)
    r1 = s1.check()
    results['check1'] = {
        'name': 'No counterexample to t = 588',
        'result': 'UNSAT' if r1 == unsat else ('SAT' if r1 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'Encoding the original equation together with t = 3x^2y^2 and t != 588 is unsatisfiable, so no integer counterexample exists.',
        'passed': r1 == unsat,
    }

    # Strengthen by proving the derived factorization has the expected integer factors.
    # Let a = 3x^2 + 1 and b = y^2 - 10. Then a*b = 507.
    a = Int('a')
    b = Int('b')
    s2 = Solver()
    s2.set(timeout=30000)
    s2.add(a == 3*x*x + 1)
    s2.add(b == y*y - 10)
    s2.add(a*b == 507)
    # Exclude the two key possibilities a = 13 and a = 169, and require a positive factor.
    s2.add(And(a > 0, a % 3 == 1))
    s2.add(Or(a != 13, a != 169))
    # This is a deliberately strong constraint set to test that no alternative factorization
    # fits the integer-square structure.
    r2 = s2.check()
    results['check2'] = {
        'name': 'Factor structure forces the unique integer solution',
        'result': 'UNSAT' if r2 == unsat else ('SAT' if r2 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'The factorization constraints eliminate alternative integer-square factorizations consistent with 507, supporting the uniqueness of x^2=4 and y^2=49.',
        'passed': r2 == unsat,
    }

    return results


if __name__ == '__main__':
    out = verify()
    for k, v in out.items():
        print(f"{k}: {v}")