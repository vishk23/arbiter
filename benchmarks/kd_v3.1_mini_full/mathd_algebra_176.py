import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified symbolic proof using kdrag/Z3: polynomial identity over reals.
    x = Real("x")
    lhs = (x + 1) * (x + 1) * x
    rhs = x * x * x + 2 * x * x + x
    try:
        proof = kd.prove(ForAll([x], lhs == rhs))
        checks.append({
            "name": "polynomial_identity_kdrag",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {proof}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "polynomial_identity_kdrag",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # SymPy symbolic expansion cross-check.
    xs = sp.symbols('x')
    expanded = sp.expand((xs + 1)**2 * xs)
    expected = xs**3 + 2*xs**2 + xs
    sympy_ok = sp.simplify(expanded - expected) == 0
    checks.append({
        "name": "sympy_expand_check",
        "passed": bool(sympy_ok),
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"expand((x+1)^2*x) = {expanded}; expected = {expected}",
    })
    if not sympy_ok:
        proved = False

    # Numerical sanity check at a concrete value.
    val = 3
    lhs_num = ((val + 1) ** 2) * val
    rhs_num = (val ** 3) + 2 * (val ** 2) + val
    num_ok = lhs_num == rhs_num
    checks.append({
        "name": "numerical_sanity_at_3",
        "passed": bool(num_ok),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"lhs={lhs_num}, rhs={rhs_num} at x=3",
    })
    if not num_ok:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)