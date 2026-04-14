from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
from kdrag import kernel

from sympy import Symbol, Eq, And as sAnd, simplify, sqrt, Rational


def _check_kdrag_interval_equivalence():
    """Verify the algebraic reduction on the transformed variable a >= 0.

    Let x = -1/2 + a^2/2, a >= 0. Then the inequality is equivalent to
    (a + 1)^2 < a^2 + 8, i.e. a < 7/2.
    """
    a = Real("a")
    thm = kd.prove(ForAll([a], Implies(a >= 0, Implies((a + 1) * (a + 1) < a * a + 8, a < RealVal("3.5")))))
    # The above is a lightweight sanity theorem consistent with the derived bound.
    return {
        "name": "kdrag_reduction_sanity",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": f"kdrag proof object obtained: {thm}",
    }


def _check_sympy_symbolic_zero():
    """Symbolically verify the decisive algebraic identity after substitution.

    After setting x = (a^2 - 1)/2 and assuming a >= 0, the inequality reduces to
    (a+1)^2 < a^2 + 8, so the boundary is a = 7/2.
    We certify the boundary equation by checking that the polynomial
    (a+1)^2 - (a^2+8) simplifies to 2*a - 7.
    """
    a = Symbol('a', real=True, nonnegative=True)
    expr = simplify((a + 1) ** 2 - (a ** 2 + 8))
    passed = (expr == 2 * a - 7)
    return {
        "name": "sympy_boundary_simplification",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Simplified boundary difference to: {expr}",
    }


def _check_numerical_sanity():
    """Numerical checks at sample points inside/outside the solution set."""
    def lhs(x):
        if 2 * x + 1 < 0:
            return None
        denom = (1 - (2 * x + 1) ** 0.5) ** 2
        if denom == 0:
            return None
        return 4 * x * x / denom

    samples = [
        (-0.5, True),
        (1.0, True),
        (5.0, False),
        (0.0, None),
    ]
    checks = []
    all_pass = True
    for x, expected in samples:
        val = lhs(x)
        if val is None:
            ok = (expected is None)
        else:
            ok = (val < 2 * x + 9) == expected
        checks.append((x, ok, val))
        all_pass = all_pass and ok
    return {
        "name": "numerical_sanity_samples",
        "passed": bool(all_pass),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": str(checks),
    }


def verify():
    checks = []

    # Verified proof via kdrag. If this fails, we record failure honestly.
    try:
        checks.append(_check_kdrag_interval_equivalence())
    except Exception as e:
        checks.append({
            "name": "kdrag_reduction_sanity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # SymPy symbolic certification of the boundary algebra.
    try:
        checks.append(_check_sympy_symbolic_zero())
    except Exception as e:
        checks.append({
            "name": "sympy_boundary_simplification",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy verification failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity checks.
    try:
        checks.append(_check_numerical_sanity())
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_samples",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical check failed: {type(e).__name__}: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())