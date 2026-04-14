from z3 import *


def verify():
    results = {}

    # Check 1: Verify domain of the expression is exactly [-1, 1].
    x = Real('x')
    domain = And(x >= -1, x <= 3, x + 1 >= 0, 3 - x >= 0, 
                 sqrt_available := True)
    # For the outer sqrt to be defined: inner quantity >= 0
    inner = And(x >= -1, x <= 3, 3 - x >= x + 1)
    s1 = Solver()
    s1.add(inner)
    # Prove equivalence to x in [-1,1]
    s1.push()
    s1.add(Not(And(x >= -1, x <= 1)))
    r1 = s1.check()
    s1.pop()
    # Counterexample to the converse: x in [-1,1] should satisfy the domain
    s1.add(And(x >= -1, x <= 1, Not(inner)))
    r1b = s1.check()
    domain_ok = (r1 == unsat) and (r1b == unsat)
    results['check1'] = {
        'name': 'Domain of the nested square roots is exactly [-1,1]',
        'result': 'UNSAT' if domain_ok else 'UNKNOWN',
        'expected': 'UNSAT',
        'explanation': 'The domain constraints are equivalent to -1 <= x <= 1.',
        'passed': domain_ok,
    }

    # Check 2: Prove the function f(x) = sqrt(sqrt(3-x)-sqrt(x+1)) is decreasing on [-1,1].
    # Since Z3 does not handle transcendental square roots directly, we prove monotonicity
    # of the inner expression g(x)=sqrt(3-x)-sqrt(x+1) by algebraic comparison after setting
    # a = sqrt(3-x), b = sqrt(x+1), with a,b >= 0 and a^2 + b^2 = 4.
    x1, x2 = Reals('x1 x2')
    a1, b1, a2, b2 = Reals('a1 b1 a2 b2')
    s2 = Solver()
    s2.set(timeout=30000)
    s2.add(x1 >= -1, x1 <= 1, x2 >= -1, x2 <= 1, x1 < x2)
    s2.add(a1 >= 0, b1 >= 0, a2 >= 0, b2 >= 0)
    s2.add(a1*a1 == 3 - x1, b1*b1 == x1 + 1)
    s2.add(a2*a2 == 3 - x2, b2*b2 == x2 + 1)
    # Violation of monotonicity: g(x1) <= g(x2) is possible only if a1-b1 <= a2-b2.
    # We ask for a counterexample to strict decrease.
    s2.add(a1 - b1 <= a2 - b2)
    r2 = s2.check()
    mono_ok = (r2 == unsat)
    results['check2'] = {
        'name': 'Inner expression is strictly decreasing on [-1,1]',
        'result': 'UNSAT' if mono_ok else ('SAT' if r2 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'No counterexample exists to strict decrease under the algebraic encoding.',
        'passed': mono_ok,
    }

    # Check 3: Verify the boundary value x = 1 - sqrt(127)/32 makes equality hold.
    # We avoid nested radicals by verifying the squared-derived quadratic relation.
    x = Real('x')
    s3 = Solver()
    s3.add(1024*x*x - 2048*x + 897 == 0)
    s3.add(x == 1 - RealVal(1)/32 * sqrt(127) if False else True)
    # Instead, directly check that x = 1 - sqrt(127)/32 satisfies the quadratic exactly.
    # Represent sqrt(127) via y where y^2 = 127 and y >= 0.
    y = Real('y')
    s3 = Solver()
    s3.add(y >= 0, y*y == 127)
    s3.add(x == 1 - y/32)
    s3.add(1024*x*x - 2048*x + 897 != 0)
    r3 = s3.check()
    boundary_ok = (r3 == unsat)
    results['check3'] = {
        'name': 'Boundary candidate x = 1 - sqrt(127)/32 satisfies the derived quadratic',
        'result': 'UNSAT' if boundary_ok else ('SAT' if r3 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'The candidate is indeed a root of the quadratic obtained from the equality case.',
        'passed': boundary_ok,
    }

    # Check 4: Verify the larger root is the extraneous one and the smaller root is the threshold.
    # The quadratic roots are 1 ± sqrt(127)/32, so the larger root is > 1 and thus outside domain.
    y = Real('y')
    s4 = Solver()
    s4.add(y >= 0, y*y == 127)
    x_small = Real('x_small')
    x_large = Real('x_large')
    s4.add(x_small == 1 - y/32, x_large == 1 + y/32)
    s4.add(Not(And(x_small < 1, x_large > 1)))
    r4 = s4.check()
    roots_ok = (r4 == unsat)
    results['check4'] = {
        'name': 'Quadratic roots split into one valid threshold and one extraneous root',
        'result': 'UNSAT' if roots_ok else ('SAT' if r4 == sat else 'UNKNOWN'),
        'expected': 'UNSAT',
        'explanation': 'The smaller root lies below 1 and the larger root lies above 1.',
        'passed': roots_ok,
    }

    return results


if __name__ == '__main__':
    res = verify()
    for k, v in res.items():
        print(f"{k}: {v}")