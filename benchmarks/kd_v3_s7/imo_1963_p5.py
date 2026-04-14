import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved_all = True

    # Verified symbolic proof using SymPy's exact algebraic-number machinery.
    # Let
    #   S = cos(pi/7) - cos(2pi/7) + cos(3pi/7)
    # and compare S - 1/2.
    # SymPy can certify that this expression is exactly zero by checking that
    # its minimal polynomial is x, i.e. the only root is 0.
    expr = sp.cos(sp.pi/7) - sp.cos(2*sp.pi/7) + sp.cos(3*sp.pi/7) - sp.Rational(1, 2)
    x = sp.Symbol('x')
    try:
        mp = sp.minimal_polynomial(expr, x)
        passed = (mp == x)
        details = f"minimal_polynomial(expr - 1/2, x) = {mp}"
    except Exception as e:
        passed = False
        details = f"SymPy minimal_polynomial computation failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "symbolic_exact_identity",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    })
    proved_all = proved_all and passed

    # Numerical sanity check at a concrete value of the exact expression.
    try:
        numeric_val = sp.N(sp.cos(sp.pi/7) - sp.cos(2*sp.pi/7) + sp.cos(3*sp.pi/7), 50)
        target = sp.N(sp.Rational(1, 2), 50)
        passed_num = sp.Abs(numeric_val - target) < sp.Float('1e-45')
        details_num = f"value={numeric_val}, target={target}, abs_err={sp.Abs(numeric_val-target)}"
    except Exception as e:
        passed_num = False
        details_num = f"Numerical evaluation failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "numerical_sanity_check",
        "passed": passed_num,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details_num,
    })
    proved_all = proved_all and passed_num

    # A small exact trigonometric consistency check using a standard identity.
    # cos(5pi/7) = -cos(2pi/7), which supports the standard rearrangement in the hint.
    try:
        exact_ok = sp.simplify(sp.cos(5*sp.pi/7) + sp.cos(2*sp.pi/7)) == 0
        details_exact = "simplify(cos(5*pi/7) + cos(2*pi/7)) == 0"
    except Exception as e:
        exact_ok = False
        details_exact = f"Exact trig simplification failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "trig_rearrangement_consistency",
        "passed": exact_ok,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details_exact,
    })
    proved_all = proved_all and exact_ok

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)