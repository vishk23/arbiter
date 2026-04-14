import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: Verified symbolic proof via kdrag/Z3 of the polynomial identity.
    # We prove the universally quantified equality:
    #   (x + 1)^2 * x = x^3 + 2*x^2 + x
    # over the reals (and hence over integers/rationals as well).
    x = Real("x")
    try:
        thm = kd.prove(ForAll([x], (x + 1) * (x + 1) * x == x * x * x + 2 * x * x + x))
        checks.append({
            "name": "polynomial_expansion_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "polynomial_expansion_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Check 2: SymPy symbolic expansion sanity check.
    # This is not the primary proof certificate, but provides an exact symbolic check.
    xs = sp.symbols('x')
    expr = sp.expand((xs + 1) ** 2 * xs)
    expected = xs**3 + 2 * xs**2 + xs
    sympy_ok = sp.simplify(expr - expected) == 0
    checks.append({
        "name": "sympy_expand_matches_expected",
        "passed": bool(sympy_ok),
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"sp.expand((x+1)**2 * x) = {expr}; expected = {expected}",
    })
    if not sympy_ok:
        proved = False

    # Check 3: Numerical sanity check at a concrete value.
    xv = 3
    lhs = (xv + 1) ** 2 * xv
    rhs = xv ** 3 + 2 * xv ** 2 + xv
    num_ok = lhs == rhs
    checks.append({
        "name": "numerical_sanity_at_x_equals_3",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"lhs={(xv + 1) ** 2 * xv}, rhs={xv ** 3 + 2 * xv ** 2 + xv}",
    })
    if not num_ok:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)