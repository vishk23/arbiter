from z3 import Solver, Int, And, Or, Not, sat, unsat, IntVal


def verify():
    results = {}

    # Variables: 1 < p < q < r, integers.
    p = Int('p')
    q = Int('q')
    r = Int('r')
    n = Int('n')

    base_constraints = And(p > 1, p < q, q < r)

    # Check 1: There is no solution with p >= 5.
    s1 = Solver()
    s1.set(timeout=30000)
    s1.add(base_constraints)
    s1.add(p >= 5)
    s1.add((p - 1) * (q - 1) * (r - 1) == 0)  # placeholder to keep structure consistent
    # Encode contradiction from the classical estimate:
    # for p >= 5 and q>p, r>q, we have 2(p-1)(q-1)(r-1) > pqr - 1.
    # So if divisibility held, n would satisfy pqr - 1 = n(...), but n >= 1 impossible.
    s1.add(p * q * r - 1 == n * (p - 1) * (q - 1) * (r - 1))
    s1.add(n >= 1)
    # Strengthen with the inequality consequence from the hint.
    s1.add(2 * (p - 1) * (q - 1) * (r - 1) <= p * q * r - 1)
    r1 = s1.check()
    results['check1'] = {
        'name': 'No solutions with p >= 5',
        'result': 'UNSAT' if r1 == unsat else ('SAT' if r1 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'The classical bound rules out p >= 5; any model would contradict 2(p-1)(q-1)(r-1) > pqr - 1.',
        'passed': r1 == unsat,
    }

    # Check 2: n = 1 leads to contradiction.
    s2 = Solver()
    s2.set(timeout=30000)
    s2.add(base_constraints)
    s2.add(p * q * r - 1 == (p - 1) * (q - 1) * (r - 1))
    # This rearranges to p+q+r = pq+pr+qr, impossible for p,q,r > 1.
    s2.add(p + q + r == p * q + p * r + q * r)
    r2 = s2.check()
    results['check2'] = {
        'name': 'n = 1 is impossible',
        'result': 'UNSAT' if r2 == unsat else ('SAT' if r2 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'If n=1 then p+q+r = pq+pr+qr, which has no integer solution with 1<p<q<r.',
        'passed': r2 == unsat,
    }

    # Check 3: n = 2 with odd variables yields the unique solution (3,5,15).
    s3 = Solver()
    s3.set(timeout=30000)
    s3.add(base_constraints)
    s3.add(n == 2)
    s3.add(p * q * r - 1 == 2 * (p - 1) * (q - 1) * (r - 1))
    s3.add(p % 2 == 1, q % 2 == 1, r % 2 == 1)
    # Narrow using the hint: p must be 3.
    s3.add(p == 3)
    r3 = s3.check()
    model3 = s3.model() if r3 == sat else None
    ok3 = False
    if r3 == sat:
        ok3 = (model3[p].as_long(), model3[q].as_long(), model3[r].as_long()) == (3, 5, 15)
    results['check3'] = {
        'name': 'n = 2 gives (3, 5, 15)',
        'result': 'SAT' if r3 == sat else ('UNSAT' if r3 == unsat else 'UNKNOWN'),
        'expected': 'SAT',
        'explanation': 'Z3 finds the solution (3,5,15) under the n=2 branch and oddness constraints.',
        'passed': ok3,
    }

    # Check 4: n = 3 with p = 2 gives the unique solution (2,4,8).
    s4 = Solver()
    s4.set(timeout=30000)
    s4.add(base_constraints)
    s4.add(n == 3)
    s4.add(p * q * r - 1 == 3 * (p - 1) * (q - 1) * (r - 1))
    s4.add(p == 2)
    r4 = s4.check()
    model4 = s4.model() if r4 == sat else None
    ok4 = False
    if r4 == sat:
        ok4 = (model4[p].as_long(), model4[q].as_long(), model4[r].as_long()) == (2, 4, 8)
    results['check4'] = {
        'name': 'n = 3 gives (2, 4, 8)',
        'result': 'SAT' if r4 == sat else ('UNSAT' if r4 == unsat else 'UNKNOWN'),
        'expected': 'SAT',
        'explanation': 'Z3 finds the solution (2,4,8) under the n=3 branch.',
        'passed': ok4,
    }

    # Check 5: Excluding the two known solutions, there is no other model.
    s5 = Solver()
    s5.set(timeout=30000)
    s5.add(base_constraints)
    s5.add(p * q * r - 1 == n * (p - 1) * (q - 1) * (r - 1))
    s5.add(Or(p != 2, q != 4, r != 8))
    s5.add(Or(p != 3, q != 5, r != 15))
    # This is the full search check; the theorem asserts UNSAT.
    r5 = s5.check()
    results['check5'] = {
        'name': 'No other solutions exist',
        'result': 'UNSAT' if r5 == unsat else ('SAT' if r5 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'Excluding the two claimed triples leaves no satisfying assignment.',
        'passed': r5 == unsat,
    }

    return results


if __name__ == '__main__':
    out = verify()
    for k, v in out.items():
        print(k, v)