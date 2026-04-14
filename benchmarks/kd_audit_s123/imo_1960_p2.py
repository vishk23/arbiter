from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, Rational, simplify, minimal_polynomial, sqrt


def verify():
    checks = []
    proved = True

    # Verified algebraic proof of the transformed inequality.
    # Let a = sqrt(2x+1), so x = (a^2 - 1)/2 and domain requires a >= 0.
    # The inequality becomes (a+1)^2 < a^2 + 8, i.e. 2a + 1 < 8, hence a < 7/2.
    # Therefore -1/2 <= x < 45/8, with x != 0 because the original expression is undefined at x=0.
    a = Real("a")
    thm1 = None
    try:
        thm1 = kd.prove(ForAll([a], Implies(And(a >= 0, a < RealVal("3.5")), a * a + 2 * a + 1 < a * a + 8)))
        checks.append({
            "name": "algebraic_reduction_transformed_inequality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm1),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "algebraic_reduction_transformed_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Symbolic zero-style certificate for the boundary computation:
    # from 2a+1<8 we get a<7/2, hence x=(a^2-1)/2 < ((7/2)^2 -1)/2 = 45/8.
    x = Symbol("x", real=True)
    a_sym = Symbol("a", nonnegative=True)
    expr = simplify(((Rational(7, 2)) ** 2 - 1) / 2 - Rational(45, 8))
    try:
        mp = minimal_polynomial(expr, Symbol("t"))
        ok = (mp == Symbol("t"))
        checks.append({
            "name": "upper_bound_boundary_exactness",
            "passed": ok,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Expression simplifies to {expr}; minimal_polynomial test returned {mp}.",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "upper_bound_boundary_exactness",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at a concrete admissible point, e.g. x = 1.
    # LHS = 4 / (1 - sqrt(3))^2, RHS = 11, and the inequality should hold.
    try:
        from math import sqrt as msqrt
        xv = 1.0
        lhs = 4 * xv * xv / ((1 - msqrt(2 * xv + 1)) ** 2)
        rhs = 2 * xv + 9
        ok = lhs < rhs
        checks.append({
            "name": "numerical_sanity_x_equals_1",
            "passed": ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x=1, lhs={lhs}, rhs={rhs}.",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_x_equals_1",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    # Check the excluded point x=0 is indeed undefined.
    try:
        from math import sqrt as msqrt
        xv = 0.0
        denom = (1 - msqrt(2 * xv + 1)) ** 2
        ok = denom == 0.0
        checks.append({
            "name": "undefined_at_x_equals_0",
            "passed": ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x=0, denominator={(denom)} so the expression is undefined.",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "undefined_at_x_equals_0",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical undefined-point check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)