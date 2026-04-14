from z3 import Solver, Int, IntVal, sat, unsat


def verify():
    results = {}

    # Let x = a_2 + a_4 + ... + a_98.
    # Since the sequence is an arithmetic progression with common difference 1,
    # we have a_{2n-1} = a_{2n} - 1 for n = 1..49.
    # Pairing terms gives:
    #   (a_1+a_2) + (a_3+a_4) + ... + (a_97+a_98)
    # = (a_2-1+a_2) + ... + (a_98-1+a_98)
    # = 2x - 49.
    # Given total sum is 137, we must have 2x - 49 = 137, hence x = 93.

    x = Int('x')
    s = Solver()
    s.set(timeout=30000)
    s.add(2 * x - 49 == 137)

    # Check that the only possible value is 93.
    s.add(x != 93)
    r = s.check()
    results['check1'] = {
        'name': 'Derive the sum of even-indexed terms',
        'result': 'UNSAT' if r == unsat else ('SAT' if r == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'If the constraints imply x != 93 is impossible, then the desired sum must be 93.',
        'passed': r == unsat,
    }

    return results


if __name__ == '__main__':
    out = verify()
    for k, v in out.items():
        print(k, v)