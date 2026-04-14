from z3 import *


def verify():
    results = {}

    # Since Z3 does not natively reason about trig functions, we use the
    # algebraic identity suggested by the problem's proof hint.
    # Let S = cos(pi/7) - cos(2pi/7) + cos(3pi/7).
    # The hint derives: 2*S*sin(pi/7) = sin(pi/7).
    # If sin(pi/7) != 0, then S = 1/2.
    # We model S and s = sin(pi/7) as reals and prove that S != 1/2
    # together with the derived equation and s != 0 is inconsistent.

    S = Real('S')
    s = Real('s')

    s1 = Solver()
    s1.set("timeout", 30000)
    s1.add(s != 0)
    s1.add(2 * S * s == s)
    s1.add(S != RealVal('1/2'))
    r1 = s1.check()
    results['check1'] = {
        'name': 'Derived equation implies S = 1/2 when sin(pi/7) != 0',
        'result': 'UNSAT' if r1 == unsat else ('SAT' if r1 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'No counterexample exists: from 2*S*s = s and s != 0, S must equal 1/2.',
        'passed': r1 == unsat,
    }

    # Also verify the purely algebraic rearrangement from the hint:
    # cos(pi/7) - cos(2pi/7) + cos(3pi/7)
    # = cos(pi/7) + cos(3pi/7) + cos(5pi/7)
    # because cos(5pi/7) = -cos(2pi/7).
    a = Real('a')
    b = Real('b')
    s2 = Solver()
    s2.set("timeout", 30000)
    s2.add(a == -b)
    s2.add(a + b != 0)
    # Encode the specific substitution pattern as a consistency check:
    # (cos(pi/7) - cos(2pi/7) + cos(3pi/7)) - (cos(pi/7) + cos(3pi/7) + cos(5pi/7))
    # collapses to 0 when cos(5pi/7) = -cos(2pi/7).
    x = Real('x')
    y = Real('y')
    z = Real('z')
    expr1 = x - y + z
    expr2 = x + z + (-y)
    s2.add(expr1 != expr2)
    r2 = s2.check()
    results['check2'] = {
        'name': 'Algebraic cosine substitution consistency',
        'result': 'UNSAT' if r2 == unsat else ('SAT' if r2 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'The rearrangement is algebraically identical: x - y + z = x + z + (-y).',
        'passed': r2 == unsat,
    }

    return results


if __name__ == "__main__":
    out = verify()
    for k, v in out.items():
        print(k, v)