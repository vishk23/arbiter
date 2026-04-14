import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Symbolic verification via SymPy expansion
    x = sp.symbols('x')
    lhs = sp.expand((x + 3) * (2 * x - 6))
    rhs = 2 * x**2 - 18
    sympy_passed = sp.simplify(lhs - rhs) == 0
    checks.append({
        "name": "sympy_expand_identity",
        "passed": bool(sympy_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"expanded lhs = {lhs}, rhs = {rhs}, difference simplifies to {sp.simplify(lhs - rhs)}",
    })
    proved = proved and bool(sympy_passed)

    # Formal proof in Z3/kdrag: expand the polynomial equality over reals.
    xr = Real("xr")
    try:
        thm = kd.prove((xr + 3) * (2 * xr - 6) == 2 * xr * xr - 18)
        kdrag_passed = True
        details = str(thm)
    except Exception as e:
        thm = None
        kdrag_passed = False
        details = f"kdrag proof failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_polynomial_identity",
        "passed": bool(kdrag_passed),
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })
    proved = proved and bool(kdrag_passed)

    # Numerical sanity check at a concrete value
    xv = 5
    num_lhs = (xv + 3) * (2 * xv - 6)
    num_rhs = 2 * xv * xv - 18
    numerical_passed = num_lhs == num_rhs
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(numerical_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"x={xv}: lhs={num_lhs}, rhs={num_rhs}",
    })
    proved = proved and bool(numerical_passed)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)