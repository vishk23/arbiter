from z3 import Solver, Real, RealVal, sat, unsat


def verify():
    results = {}

    # Unknowns
    x1, x2, x3, x4, x5, x6, x7 = [Real(f"x{i}") for i in range(1, 8)]

    # The given constraints
    eq1 = x1 + 4*x2 + 9*x3 + 16*x4 + 25*x5 + 36*x6 + 49*x7 == RealVal(1)
    eq2 = 4*x1 + 9*x2 + 16*x3 + 25*x4 + 36*x5 + 49*x6 + 64*x7 == RealVal(12)
    eq3 = 9*x1 + 16*x2 + 25*x3 + 36*x4 + 49*x5 + 64*x6 + 81*x7 == RealVal(123)

    # Define f(k) = sum_{i=1}^7 (k+i-1)^2 * x_i
    def f(k):
        ks = [k + i for i in range(0, 7)]
        xs = [x1, x2, x3, x4, x5, x6, x7]
        return sum((RealVal(k + i) * RealVal(k + i)) * xs[i] for i in range(7))

    # Check 1: There exists a solution to the given system.
    s1 = Solver()
    s1.set(timeout=30000)
    s1.add(eq1, eq2, eq3)
    r1 = s1.check()
    results["check1"] = {
        "name": "Consistency of the given linear system",
        "result": "SAT" if r1 == sat else "UNSAT" if r1 == unsat else "UNKNOWN",
        "expected": "SAT",
        "explanation": "The constraints are consistent; at least one real tuple (x1,...,x7) satisfies the three equations.",
        "passed": r1 == sat,
    }

    # Check 2: The target expression must equal 334 for all solutions.
    target = 16*x1 + 25*x2 + 36*x3 + 49*x4 + 64*x5 + 81*x6 + 100*x7
    s2 = Solver()
    s2.set(timeout=30000)
    s2.add(eq1, eq2, eq3)
    s2.add(target != RealVal(334))
    r2 = s2.check()
    results["check2"] = {
        "name": "Prove the target value is uniquely 334",
        "result": "SAT" if r2 == sat else "UNSAT" if r2 == unsat else "UNKNOWN",
        "expected": "UNSAT",
        "explanation": "No counterexample exists: under the given equations, the expression 16x1+...+100x7 cannot differ from 334.",
        "passed": r2 == unsat,
    }

    # Check 3: Verify the quadratic interpolation argument algebraically via coefficient equations.
    # Let f(k) = a k^2 + b k + c. The three given values imply a,b,c.
    a, b, c = Real('a'), Real('b'), Real('c')
    s3 = Solver()
    s3.set(timeout=30000)
    s3.add(4*a + 2*b + c == RealVal(12))
    s3.add(1*a + 1*b + c == RealVal(1))
    s3.add(9*a + 3*b + c == RealVal(123))
    s3.add(16*a + 4*b + c != RealVal(334))
    r3 = s3.check()
    results["check3"] = {
        "name": "Quadratic extrapolation gives 334",
        "result": "SAT" if r3 == sat else "UNSAT" if r3 == unsat else "UNKNOWN",
        "expected": "UNSAT",
        "explanation": "The unique quadratic fitting f(1)=1, f(2)=12, f(3)=123 has f(4)=334.",
        "passed": r3 == unsat,
    }

    return results


if __name__ == "__main__":
    out = verify()
    for k, v in out.items():
        print(k, v)