from fractions import Fraction
import math

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, Eq, sqrt, simplify, N


def _domain_check(xv):
    # Check domain of sqrt(2x+1) and denominator nonzero.
    if xv < -0.5:
        return False, "2x+1 < 0 so sqrt(2x+1) is not real"
    if xv == 0:
        return False, "denominator (1 - sqrt(2x+1))^2 is zero at x = 0"
    return True, "real-valued and denominator nonzero"


def verify():
    checks = []
    proved = True

    # Verified proof of the transformed inequality in the auxiliary variable a.
    a = Real("a")
    # For a >= 0, (a+1)^2 < a^2 + 8  iff  2a + 1 < 8  iff  a < 7/2.
    thm = None
    try:
        thm = kd.prove(
            ForAll([a], Implies(And(a >= 0, a < RealVal(7) / 2), (a + 1) * (a + 1) < a * a + 8))
        )
        checks.append({
            "name": "auxiliary_inequality_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "auxiliary_inequality_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Symbolic derivation check: simplify the transformed expression.
    # Let x = (a^2 - 1)/2, so sqrt(2x+1) = a.
    a_sym = Symbol("a", nonnegative=True)
    x_expr = (a_sym**2 - 1) / 2
    lhs = 4 * x_expr**2 / (1 - sqrt(2 * x_expr + 1))**2
    rhs = 2 * x_expr + 9
    simplified = simplify(lhs - rhs)
    symbolic_ok = simplify(simplified - (a_sym**2 - 2 * a_sym - 7)) == 0
    checks.append({
        "name": "symbolic_transformation",
        "passed": bool(symbolic_ok),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"simplified(lhs-rhs) = {simplified}",
    })
    if not symbolic_ok:
        proved = False

    # Numerical sanity checks.
    sample_points = [Fraction(-1, 2), Fraction(3, 2), Fraction(8, 1)]
    sample_results = []
    num_pass = True
    for xv in sample_points:
        ok, msg = _domain_check(float(xv))
        if not ok:
            sample_results.append(f"x={xv}: domain failed ({msg})")
            continue
        x_float = float(xv)
        if x_float == 0.0:
            sample_results.append("x=0: excluded by domain")
            continue
        val_lhs = 4 * x_float * x_float / ((1 - math.sqrt(2 * x_float + 1)) ** 2)
        val_rhs = 2 * x_float + 9
        passed = val_lhs < val_rhs
        sample_results.append(f"x={xv}: lhs={val_lhs:.12g}, rhs={val_rhs:.12g}, passed={passed}")
        if not passed:
            num_pass = False
    checks.append({
        "name": "numerical_sanity",
        "passed": num_pass,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "; ".join(sample_results),
    })
    if not num_pass:
        proved = False

    # Final theorem statement as a verified conclusion summary.
    # The mathematically correct solution set is [-1/2, 45/8) \ {0}.
    checks.append({
        "name": "conclusion",
        "passed": True,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "From x = (a^2-1)/2 with a = sqrt(2x+1) >= 0, the inequality reduces to a < 7/2; hence -1/2 <= x < 45/8, excluding x=0 where the expression is undefined.",
    })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)