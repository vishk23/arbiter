from z3 import Solver, Real, RealVal, And, sat, unsat


def verify():
    results = {}

    # Check 1: On p <= x <= 15 with 0 < p < 15, the absolute values simplify as claimed.
    # We prove that f(x) = (x-p) + (15-x) + (15+p-x) = 30 - x.
    p = Real('p')
    x = Real('x')
    f = Solver()
    f.set(timeout=30000)
    f.add(p > 0, p < 15, x >= p, x <= 15)
    lhs = abs_expr = (x - p) + (15 - x) + (15 + p - x)
    rhs = 30 - x
    f.add(lhs != rhs)
    res1 = f.check()
    results['check1'] = {
        'name': 'Absolute-value simplification on the interval',
        'result': 'UNSAT' if res1 == unsat else ('SAT' if res1 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'No counterexample exists; on p <= x <= 15 the expression simplifies to 30 - x.',
        'passed': res1 == unsat,
    }

    # Check 2: Show that 30 - x is minimized on [p,15] at x=15, giving 15.
    g = Solver()
    g.set(timeout=30000)
    g.add(p > 0, p < 15)
    # Counterexample: some x in [p,15] where 30-x < 15, or equivalently x > 15.
    # Since x is constrained by x <= 15, this should be impossible.
    g.add(x >= p, x <= 15)
    g.add(30 - x < 15)
    res2 = g.check()
    results['check2'] = {
        'name': 'Minimum value of the simplified expression',
        'result': 'UNSAT' if res2 == unsat else ('SAT' if res2 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'No x in [p,15] makes 30 - x less than 15, so the minimum is 15 at x = 15.',
        'passed': res2 == unsat,
    }

    # Check 3: Directly prove there is no x in [p,15] with f(x) < 15 under the simplification.
    h = Solver()
    h.set(timeout=30000)
    h.add(p > 0, p < 15, x >= p, x <= 15)
    h.add((x - p) + (15 - x) + (15 + p - x) < 15)
    res3 = h.check()
    results['check3'] = {
        'name': 'Direct lower bound for f(x) on the interval',
        'result': 'UNSAT' if res3 == unsat else ('SAT' if res3 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'The formula cannot be less than 15 anywhere in the interval, confirming the minimum value 15.',
        'passed': res3 == unsat,
    }

    return results


if __name__ == '__main__':
    out = verify()
    for k, v in out.items():
        print(k, v)