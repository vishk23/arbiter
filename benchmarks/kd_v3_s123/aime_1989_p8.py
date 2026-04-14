import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof via SymPy linear algebra.
    # We model the three given equations and the target expression using exact rationals.
    x = sp.symbols('x1:8', real=True)
    A = sp.Matrix([
        [1, 4, 9, 16, 25, 36, 49],
        [4, 9, 16, 25, 36, 49, 64],
        [9, 16, 25, 36, 49, 64, 81],
    ])
    b = sp.Matrix([1, 12, 123])
    target = sp.Matrix([16, 25, 36, 49, 64, 81, 100])

    # Use a concrete exact solution from linsolve and verify the target is invariant.
    sol = next(iter(sp.linsolve((A, b), x)))
    target_value = sp.simplify(target.dot(sp.Matrix(sol)))
    sympy_pass = (target_value == sp.Integer(334))
    checks.append({
        "name": "sympy_linear_algebra_target_value",
        "passed": bool(sympy_pass),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Exact linear solve gives target expression = {target_value}; expected 334.",
    })
    proved = proved and bool(sympy_pass)

    # Check 2: kdrag proof certificate for the quadratic interpolation step.
    # Let f(k) = a*k^2 + b*k + c. From f(1)=1, f(2)=12, f(3)=123, prove f(4)=334.
    k = Int('k')
    a, b_, c = Ints('a b c')
    f = kd.define('f', [k, a, b_, c], a * k * k + b_ * k + c)
    thm = None
    try:
        thm = kd.prove(
            ForAll([a, b_, c],
                   Implies(And(f(1, a, b_, c) == 1,
                               f(2, a, b_, c) == 12,
                               f(3, a, b_, c) == 123),
                           f(4, a, b_, c) == 334)),
            by=[f.defn]
        )
        kd_pass = True
        details = f"kd.prove succeeded with proof object: {thm}."
    except Exception as e:
        kd_pass = False
        details = f"kd.prove failed: {type(e).__name__}: {e}"
    checks.append({
        "name": "kdrag_quadratic_interpolation_certificate",
        "passed": kd_pass,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })
    proved = proved and kd_pass

    # Check 3: numerical sanity check on the reconstructed quadratic values.
    # From the given values, the unique quadratic through (1,1),(2,12),(3,123) is 50k^2 - 139k + 90.
    def q(n):
        return 50 * n * n - 139 * n + 90
    num_pass = (q(1) == 1 and q(2) == 12 and q(3) == 123 and q(4) == 334)
    checks.append({
        "name": "numerical_sanity_quadratic_values",
        "passed": bool(num_pass),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"q(1)={q(1)}, q(2)={q(2)}, q(3)={q(3)}, q(4)={q(4)}.",
    })
    proved = proved and bool(num_pass)

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)