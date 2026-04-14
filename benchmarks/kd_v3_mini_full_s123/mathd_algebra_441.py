import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof via kdrag/Z3: under x != 0, the expression equals 10.
    x = Real("x")
    expr = (12 / (x * x)) * (x**4 / (14 * x)) * (35 / (3 * x))
    theorem = ForAll([x], Implies(x != 0, expr == 10))
    try:
        proof = kd.prove(theorem)
        checks.append({
            "name": "algebraic_simplification_equals_10",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {proof}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "algebraic_simplification_equals_10",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # SymPy exact symbolic verification on a nonzero symbol.
    xs = sp.symbols('xs', nonzero=True)
    sym_expr = (12 / (xs * xs)) * (xs**4 / (14 * xs)) * (35 / (3 * xs))
    simplified = sp.simplify(sym_expr)
    sym_passed = simplified == 10
    checks.append({
        "name": "sympy_simplification_check",
        "passed": bool(sym_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"sp.simplify(...) returned {simplified}",
    })
    if not sym_passed:
        proved = False

    # Numerical sanity check at a concrete nonzero value.
    xval = 2
    numeric = (12 / (xval * xval)) * (xval**4 / (14 * xval)) * (35 / (3 * xval))
    num_passed = abs(float(numeric) - 10.0) < 1e-12
    checks.append({
        "name": "numerical_sanity_at_x_eq_2",
        "passed": bool(num_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Value at x=2 is {numeric}",
    })
    if not num_passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)