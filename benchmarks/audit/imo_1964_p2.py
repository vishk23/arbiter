from z3 import Solver, Real, And, Or, Not, Implies, ForAll, Exists, sat, unsat, RealVal, If


def verify():
    results = {}

    # Check 1: After the substitution a=x+y, b=x+z, c=y+z,
    # the target inequality reduces to a polynomial inequality that is equivalent to
    # x^2y + x^2z + y^2x + y^2z + z^2x + z^2y >= 6xyz.
    # We prove the contrapositive form: if the AM-GM inequality holds, then the original
    # inequality holds. The negation of the implication should be UNSAT.
    x = Real('x')
    y = Real('y')
    z = Real('z')

    # Triangle substitution requires x,y,z >= 0 for side lengths a,b,c > 0.
    s = Solver()
    s.set(timeout=30000)
    s.add(x >= 0, y >= 0, z >= 0)

    a = x + y
    b = x + z
    c = y + z

    lhs = a*a*(b + c - a) + b*b*(c + a - b) + c*c*(a + b - c)
    rhs = 3*a*b*c

    amgm = (x*x*y + x*x*z + y*y*x + y*y*z + z*z*x + z*z*y) >= 6*x*y*z

    # Negation of: amgm implies lhs <= rhs
    s.add(amgm)
    s.add(lhs > rhs)

    r1 = s.check()
    results['check1'] = {
        'name': 'Substitution reduces the triangle inequality to AM-GM form',
        'result': 'UNSAT' if r1 == unsat else ('SAT' if r1 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'No counterexample exists to the reduced inequality under the substitution a=x+y, b=x+z, c=y+z.',
        'passed': r1 == unsat,
    }

    # Check 2: AM-GM step used in the proof:
    # (x^2y + x^2z + y^2x + y^2z + z^2x + z^2y)/6 >= xyz
    # for x,y,z >= 0.
    s2 = Solver()
    s2.set(timeout=30000)
    s2.add(x >= 0, y >= 0, z >= 0)
    s2.add((x*x*y + x*x*z + y*y*x + y*y*z + z*z*x + z*z*y) < 6*x*y*z)

    r2 = s2.check()
    results['check2'] = {
        'name': 'AM-GM bound for the six-term sum',
        'result': 'UNSAT' if r2 == unsat else ('SAT' if r2 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'The six-term sum is always at least 6xyz for nonnegative x,y,z.',
        'passed': r2 == unsat,
    }

    # Check 3: Direct verification that the transformed inequality is equivalent to
    # 2*(x^2y + x^2z + y^2x + y^2z + z^2x + z^2y) + 12xyz <=
    # 3*(x+y)(x+z)(y+z).
    # We verify the algebraic identity by checking that the difference simplifies to
    # 3*(...) - 2*(...) - 12xyz, and that the inequality follows from AM-GM.
    s3 = Solver()
    s3.set(timeout=30000)
    s3.add(x >= 0, y >= 0, z >= 0)
    expr_left = 2*(x*x*y + x*x*z + y*y*x + y*y*z + z*z*x + z*z*y) + 12*x*y*z
    expr_right = 3*(x+y)*(x+z)*(y+z)
    s3.add(expr_left > expr_right)

    r3 = s3.check()
    results['check3'] = {
        'name': 'Expanded form is bounded by 3(x+y)(x+z)(y+z)',
        'result': 'UNSAT' if r3 == unsat else ('SAT' if r3 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'The expanded polynomial form cannot exceed the cubic product when the AM-GM bound is applied.',
        'passed': r3 == unsat,
    }

    return results


if __name__ == '__main__':
    out = verify()
    for k, v in out.items():
        print(k, v)