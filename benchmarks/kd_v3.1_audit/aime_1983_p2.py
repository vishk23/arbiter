from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
import sympy as sp


# The theorem: for 0 < p < 15 and p <= x <= 15,
# f(x) = |x-p| + |x-15| + |x-p-15| has minimum value 15 on [p, 15].


def verify():
    checks = []
    proved = True

    # ------------------------------------------------------------------
    # Verified proof 1 (kdrag): algebraic simplification on the interval
    # ------------------------------------------------------------------
    x = Real("x")
    p = Real("p")

    # On the interval p <= x <= 15 and with p > 0:
    # x - p >= 0, x - 15 <= 0, x - p - 15 < 0
    # so f(x) = (x-p) + (15-x) + (p+15-x) = 30 - x.
    # We prove the algebraic identity that the simplified expression equals 30 - x.
    try:
        simpl_thm = kd.prove(
            ForAll([x, p],
                   Implies(And(p > 0, p <= x, x <= 15),
                           (If(x - p >= 0, x - p, p - x) +
                            If(x - 15 >= 0, x - 15, 15 - x) +
                            If(x - p - 15 >= 0, x - p - 15, p + 15 - x)) == 30 - x))
        )
        checks.append({
            "name": "interval_simplification_to_30_minus_x",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proved a certificate: {simpl_thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "interval_simplification_to_30_minus_x",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # ------------------------------------------------------------------
    # Verified proof 2 (kdrag): minimum of 30 - x on [p,15] is 15 at x=15
    # Since x <= 15 implies 30 - x >= 15, and at x = 15 it equals 15.
    # ------------------------------------------------------------------
    try:
        min_thm = kd.prove(
            ForAll([x], Implies(And(x >= 0, x <= 15), 30 - x >= 15))
        )
        eq_thm = kd.prove(30 - 15 == 15)
        checks.append({
            "name": "minimum_of_30_minus_x_on_interval",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proved lower bound and endpoint value: {min_thm}; {eq_thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "minimum_of_30_minus_x_on_interval",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # ------------------------------------------------------------------
    # SymPy symbolic computation: simplify the expression on the interval.
    # This is not the main proof, but provides a corroborating symbolic check.
    # ------------------------------------------------------------------
    try:
        xs, ps = sp.symbols('x p', real=True)
        simplified = sp.simplify((xs - ps) + (15 - xs) + (ps + 15 - xs))
        passed = sp.simplify(simplified - (30 - xs)) == 0
        checks.append({
            "name": "sympy_symbolic_simplification",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Simplified expression is {simplified}; difference from 30 - x is {sp.simplify(simplified - (30 - xs))}.",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "sympy_symbolic_simplification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic check failed: {type(e).__name__}: {e}",
        })

    # ------------------------------------------------------------------
    # Numerical sanity check: pick a concrete p and x in the interval.
    # Example p=7, x=15 gives f(15)=15.
    # Also check an interior point x=10 gives a larger value.
    # ------------------------------------------------------------------
    try:
        p0 = Fraction(7, 1)
        x1 = Fraction(15, 1)
        x2 = Fraction(10, 1)

        def fval(xv, pv):
            return abs(xv - pv) + abs(xv - 15) + abs(xv - pv - 15)

        v1 = fval(x1, p0)
        v2 = fval(x2, p0)
        passed = (v1 == 15) and (v2 >= 15)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For p=7: f(15)={v1}, f(10)={v2}.",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)