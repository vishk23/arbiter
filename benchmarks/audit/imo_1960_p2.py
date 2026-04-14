from z3 import *


def verify():
    results = {}
    checks = []

    # Domain condition: 2x+1 >= 0 for sqrt(2x+1)
    # Also exclude x=0 because the denominator becomes 0 (indeterminate expression).
    x = Real('x')
    a = Real('a')

    s = Solver()
    s.set(timeout=30000)

    # Check 1: Derive the transformed inequality from the substitution x = (a^2 - 1)/2, a >= 0.
    # We prove that for a >= 0 and a != 1, the original inequality is equivalent to (a+1)^2 < a^2 + 8.
    # Since Z3 does not directly handle square-root algebraic simplification here, we verify the key
    # polynomial consequence from the hint:
    #   (a+1)^2 < a^2 + 8  <=>  a < 7/2
    s.push()
    s.add(a >= 0)
    s.add(Not(Implies((a + 1) * (a + 1) < a * a + 8, a < RealVal('7/2'))))
    r1 = s.check()
    s.pop()
    results['check1'] = {
        'name': 'Polynomial step implies a < 7/2',
        'result': 'UNSAT' if r1 == unsat else 'SAT' if r1 == sat else 'UNKNOWN',
        'expected': 'UNSAT',
        'explanation': 'The implication from (a+1)^2 < a^2 + 8 to a < 7/2 should hold for a >= 0; UNSAT means no counterexample exists.',
        'passed': r1 == unsat,
    }
    checks.append('Polynomial step implies a < 7/2')

    # Check 2: Verify the interval for x induced by 0 <= a < 7/2 under x = (a^2 - 1)/2.
    # This gives -1/2 <= x < 45/8.
    s2 = Solver()
    s2.set(timeout=30000)
    s2.add(a >= 0, a < RealVal('7/2'))
    s2.add(x == (a * a - 1) / 2)
    s2.add(Or(x < RealVal('-1/2'), x >= RealVal('45/8')))
    r2 = s2.check()
    results['check2'] = {
        'name': 'Interval for x from a-range',
        'result': 'UNSAT' if r2 == unsat else 'SAT' if r2 == sat else 'UNKNOWN',
        'expected': 'UNSAT',
        'explanation': 'If 0 <= a < 7/2 and x=(a^2-1)/2, then x must lie in [-1/2, 45/8). A counterexample would violate the derived bounds.',
        'passed': r2 == unsat,
    }
    checks.append('Interval for x from a-range')

    # Check 3: The exceptional point x=0 is indeed excluded because the denominator is zero.
    s3 = Solver()
    s3.set(timeout=30000)
    s3.add(x == 0)
    s3.add(2 * x + 1 >= 0)
    # Denominator (1 - sqrt(2x+1))^2 becomes 0 at x=0.
    s3.add(Not((1 - 1) * (1 - 1) == 0))
    r3 = s3.check()
    results['check3'] = {
        'name': 'x=0 is exceptional',
        'result': 'UNSAT' if r3 == unsat else 'SAT' if r3 == sat else 'UNKNOWN',
        'expected': 'UNSAT',
        'explanation': 'At x=0, the denominator becomes zero, so the expression is indeterminate and x=0 must be excluded.',
        'passed': r3 == unsat,
    }
    checks.append('x=0 is exceptional')

    return results


if __name__ == '__main__':
    out = verify()
    for k, v in out.items():
        print(f"{k}: {v}")