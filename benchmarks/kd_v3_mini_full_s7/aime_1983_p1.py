import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Symbolic/numerical pre-check via SymPy: derive the expected answer from the linearized equations.
    A = sp.symbols('A', positive=True)
    p = A / 24
    q = A / 40
    r = A / 12 - p - q
    ans = sp.simplify(A / r)
    sympy_check_passed = (ans == 60)
    checks.append({
        "name": "sympy_linearized_solution",
        "passed": bool(sympy_check_passed),
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"Linearized substitution yields A/r = {ans}; expected 60.",
    })
    proved = proved and bool(sympy_check_passed)

    # Verified proof in kdrag: prove the equivalent rational identity.
    # Let a = ln(w) > 0, p = ln(x), q = ln(y), r = ln(z).
    # Then p = a/24, q = a/40, and p+q+r = a/12, hence r = a/60.
    # Therefore log_z w = a/r = 60.
    a = Real("a")
    r = Real("r")

    thm = None
    try:
        thm = kd.prove(ForAll([a], Implies(a > 0, (a / (a / 60)) == 60)))
        checks.append({
            "name": "kdrag_rational_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {thm}",
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_rational_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof attempt failed: {type(e).__name__}: {e}",
        })
        proved = False

    # Direct algebraic certificate of the key linear relation r = a/60.
    try:
        lin = kd.prove(ForAll([a], Implies(a > 0, ((a / 12) - (a / 24) - (a / 40)) == (a / 60))))
        checks.append({
            "name": "kdrag_key_linear_relation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {lin}",
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_key_linear_relation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof attempt failed: {type(e).__name__}: {e}",
        })
        proved = False

    # Numerical sanity check with a concrete choice.
    # Choose w = e^120, then x = e^5, y = e^3, z = e^2, giving log_z(w) = 60.
    num_val = sp.N(sp.log(sp.E ** 120) / sp.log(sp.E ** 2))
    num_passed = sp.simplify(num_val - 60) == 0
    checks.append({
        "name": "numerical_sanity_example",
        "passed": bool(num_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Concrete example gives log_z(w) = {num_val}.",
    })
    proved = proved and bool(num_passed)

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)