import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # ------------------------------------------------------------
    # Check 1: symbolic verification that the reduced equation has
    # the claimed value y = 104, via exact rational arithmetic.
    # ------------------------------------------------------------
    try:
        y = sp.Symbol('y')
        expr = sp.together(1/(y - 29) + 1/(y - 45) - 2/(y - 69))
        num, den = sp.fraction(sp.simplify(expr))
        # Substitute y = 104 and verify the numerator is exactly zero.
        num_at_104 = sp.expand(num.subs(y, 104))
        symbolic_ok = sp.simplify(num_at_104) == 0
        checks.append({
            "name": "symbolic_reduction_y_equals_104",
            "passed": bool(symbolic_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Reduced expression numerator at y=104 simplifies to {num_at_104}."
        })
        proved = proved and bool(symbolic_ok)
    except Exception as e:
        checks.append({
            "name": "symbolic_reduction_y_equals_104",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy computation failed: {e}"
        })
        proved = False

    # ------------------------------------------------------------
    # Check 2: verified certificate using kdrag for the algebraic
    # step that the equation in y is equivalent to 64*y = 6656.
    # We prove the polynomial identity after clearing denominators.
    # ------------------------------------------------------------
    try:
        Y = Int('Y')
        # The cleared-denominator numerator for
        # 1/(Y-29)+1/(Y-45)-2/(Y-69) is:
        # (Y-45)(Y-69) + (Y-29)(Y-69) - 2(Y-29)(Y-45)
        poly = (Y - 45) * (Y - 69) + (Y - 29) * (Y - 69) - 2 * (Y - 29) * (Y - 45)
        thm = kd.prove(ForAll([Y], poly == -64 * Y + 6656))
        checks.append({
            "name": "kdrag_cleared_denominator_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove established ForAll(Y, cleared_numerator == -64*Y + 6656): {thm}."
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_cleared_denominator_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })
        proved = False

    # ------------------------------------------------------------
    # Check 3: exact symbolic solve for x, with positive root 13.
    # ------------------------------------------------------------
    try:
        x = sp.Symbol('x', real=True)
        sols = sp.solve(sp.Eq(x**2 - 10*x - 104, 0), x)
        positive = [s for s in sols if sp.N(s) > 0]
        ok = (13 in positive) or (sp.Integer(13) in positive)
        checks.append({
            "name": "symbolic_solve_positive_root_13",
            "passed": bool(ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solutions of x^2 - 10*x - 104 = 0 are {sols}; positive solutions filtered to {positive}."
        })
        proved = proved and bool(ok)
    except Exception as e:
        checks.append({
            "name": "symbolic_solve_positive_root_13",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy solve failed: {e}"
        })
        proved = False

    # ------------------------------------------------------------
    # Check 4: numerical sanity check at x = 13.
    # ------------------------------------------------------------
    try:
        xv = sp.Rational(13)
        val = sp.N(1/(xv**2 - 10*xv - 29) + 1/(xv**2 - 10*xv - 45) - 2/(xv**2 - 10*xv - 69), 50)
        ok = abs(complex(val)) < 1e-40
        checks.append({
            "name": "numerical_sanity_at_13",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Expression evaluated at x=13 gives {val}."
        })
        proved = proved and bool(ok)
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_at_13",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}"
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)