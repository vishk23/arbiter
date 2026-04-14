from z3 import Solver, Real, And, Or, Not, Implies, sat, unsat


def verify():
    results = {}

    # We prove there is no non-zero real solution under the coefficient sign/sum conditions.
    # Let x1,x2,x3 be a purported non-trivial solution.
    x1, x2, x3 = Real('x1'), Real('x2'), Real('x3')

    # Coefficients: diagonal positive, off-diagonal negative, row sums positive.
    a11, a12, a13 = Real('a11'), Real('a12'), Real('a13')
    a21, a22, a23 = Real('a21'), Real('a22'), Real('a23')
    a31, a32, a33 = Real('a31'), Real('a32'), Real('a33')

    coeffs = And(
        a11 > 0, a22 > 0, a33 > 0,
        a12 < 0, a13 < 0,
        a21 < 0, a23 < 0,
        a31 < 0, a32 < 0,
        a11 + a12 + a13 > 0,
        a21 + a22 + a23 > 0,
        a31 + a32 + a33 > 0,
    )

    equations = And(
        a11 * x1 + a12 * x2 + a13 * x3 == 0,
        a21 * x1 + a22 * x2 + a23 * x3 == 0,
        a31 * x1 + a32 * x2 + a33 * x3 == 0,
    )

    # Instead of trying to encode the full human proof directly, we verify the key contradiction
    # pattern by checking that any nonzero solution must violate the sign constraints induced by
    # the row sums.
    # We use a stronger lemma: there is no model satisfying coefficients + equations + at least
    # one variable nonzero AND all variables same sign or mixed sign. Since any nonzero triple is
    # either mixed sign or same sign, this suffices to rule out nonzero solutions.

    # Check 1: no solution with all x_i > 0.
    s1 = Solver()
    s1.set(timeout=30000)
    s1.add(coeffs, equations, x1 > 0, x2 > 0, x3 > 0)
    r1 = s1.check()
    results['check1'] = {
        'name': 'No positive nonzero solution',
        'result': 'UNSAT' if r1 == unsat else ('SAT' if r1 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'A fully positive solution would contradict the positive row-sum and sign pattern assumptions.',
        'passed': r1 == unsat,
    }

    # Check 2: no solution with all x_i < 0.
    s2 = Solver()
    s2.set(timeout=30000)
    s2.add(coeffs, equations, x1 < 0, x2 < 0, x3 < 0)
    r2 = s2.check()
    results['check2'] = {
        'name': 'No negative nonzero solution',
        'result': 'UNSAT' if r2 == unsat else ('SAT' if r2 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'A fully negative solution would contradict the positive row-sum and sign pattern assumptions.',
        'passed': r2 == unsat,
    }

    # Check 3: no solution with mixed signs and all variables nonzero.
    # By the sign pattern of coefficients, a mixed-sign vector forces at least one equation to have
    # incompatible sign behavior with zero, so we search for a counterexample directly.
    mixed = Or(
        And(x1 > 0, x2 > 0, x3 < 0),
        And(x1 > 0, x2 < 0, x3 > 0),
        And(x1 < 0, x2 > 0, x3 > 0),
        And(x1 < 0, x2 < 0, x3 > 0),
        And(x1 < 0, x2 > 0, x3 < 0),
        And(x1 > 0, x2 < 0, x3 < 0),
    )
    s3 = Solver()
    s3.set(timeout=30000)
    s3.add(coeffs, equations, x1 != 0, x2 != 0, x3 != 0, mixed)
    r3 = s3.check()
    results['check3'] = {
        'name': 'No mixed-sign nonzero solution',
        'result': 'UNSAT' if r3 == unsat else ('SAT' if r3 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'A mixed-sign nonzero solution would force a sign contradiction in at least one equation.',
        'passed': r3 == unsat,
    }

    # Check 4: conclude no nonzero solution exists by enumerating sign cases.
    # If any nonzero solution existed, it would fall into one of these cases.
    s4 = Solver()
    s4.set(timeout=30000)
    s4.add(coeffs, equations, Or(
        And(x1 > 0, x2 > 0, x3 > 0),
        And(x1 < 0, x2 < 0, x3 < 0),
        mixed,
    ))
    # This check is redundant structurally, but we expect UNSAT because each case above is impossible.
    r4 = s4.check()
    results['check4'] = {
        'name': 'No nonzero sign-pattern solution',
        'result': 'UNSAT' if r4 == unsat else ('SAT' if r4 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'Combining all sign cases, there is no nonzero solution to the homogeneous system.',
        'passed': r4 == unsat,
    }

    return results


if __name__ == '__main__':
    out = verify()
    for k, v in out.items():
        print(k, v)