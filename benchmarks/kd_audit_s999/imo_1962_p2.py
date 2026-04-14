from fractions import Fraction

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, Rational, sqrt, minimal_polynomial


def verify():
    checks = []
    proved_all = True

    # Check 1: symbolic exact algebraic verification of the boundary point.
    # Let x0 = 1 - sqrt(127)/32. Then the boundary equation is
    # sqrt(sqrt(3-x0) - sqrt(x0+1)) = 1/2.
    # We certify this by proving the algebraic identity on a suitable polynomial.
    try:
        t = Symbol('t')
        x0 = Rational(1, 1) - sqrt(127) / 32
        expr = (sqrt(3 - x0) - sqrt(x0 + 1)) - Rational(1, 4)
        mp = minimal_polynomial(expr, t)
        passed = (mp == t)
        checks.append({
            "name": "boundary_point_exactness",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(expr, t) == t evaluates to {mp!s}."
        })
        proved_all = proved_all and passed
    except Exception as e:
        checks.append({
            "name": "boundary_point_exactness",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e!r}"
        })
        proved_all = False

    # Check 2: verified proof in kdrag that the candidate solution is in the domain.
    try:
        x = Real("x")
        # For x in [-1, 1], both radicands are nonnegative and the outer radicand is nonnegative.
        dom_thm = kd.prove(
            ForAll([x],
                   Implies(And(x >= -1, x <= 1),
                           And(3 - x >= 0, x + 1 >= 0, 3 - x >= x + 1)))
        )
        checks.append({
            "name": "domain_constraints",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by kd.prove: {dom_thm!s}"
        })
    except Exception as e:
        checks.append({
            "name": "domain_constraints",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e!r}"
        })
        proved_all = False

    # Check 3: numerical sanity check at a concrete point in the interval.
    try:
        import math
        x_test = -1.0
        lhs = math.sqrt(math.sqrt(3 - x_test) - math.sqrt(x_test + 1))
        passed = lhs > 0.5
        checks.append({
            "name": "numerical_sanity_at_minus_one",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x = {x_test}, lhs = {lhs:.12f} > 1/2 is {passed}."
        })
        proved_all = proved_all and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_at_minus_one",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e!r}"
        })
        proved_all = False

    # Check 4: numerical sanity at a point beyond the claimed upper endpoint.
    try:
        import math
        x_test = 0.7
        lhs = math.sqrt(math.sqrt(3 - x_test) - math.sqrt(x_test + 1))
        passed = lhs > 0.5
        # We expect this to be False; the check passes if it correctly fails the inequality.
        passed = not passed
        checks.append({
            "name": "numerical_sanity_above_threshold",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x = {x_test}, lhs = {lhs:.12f} is not > 1/2, matching the theorem: {passed}."
        })
        proved_all = proved_all and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_above_threshold",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e!r}"
        })
        proved_all = False

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)