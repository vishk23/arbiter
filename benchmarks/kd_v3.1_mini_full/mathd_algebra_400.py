from fractions import Fraction

import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof using kdrag/Z3.
    # We prove that if 5 + 500% of 10 equals 110% of x, then x = 50.
    x = Real("x")
    premise = 5 + Fraction(500, 100) * 10 == Fraction(110, 100) * x
    theorem = ForAll([x], Implies(premise, x == 50))
    try:
        proof = kd.prove(theorem)
        checks.append({
            "name": "kdrag_proof_x_equals_50",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned a Proof object: {proof}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_proof_x_equals_50",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: SymPy symbolic verification that the equation solves to 50.
    xs = sp.symbols('x', real=True)
    eq = sp.Eq(5 + sp.Rational(500, 100) * 10, sp.Rational(110, 100) * xs)
    sol = sp.solve(eq, xs)
    passed_sympy = (len(sol) == 1 and sp.simplify(sol[0] - 50) == 0)
    if not passed_sympy:
        proved = False
    checks.append({
        "name": "sympy_solve_to_50",
        "passed": bool(passed_sympy),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"solve({eq}) -> {sol}",
    })

    # Check 3: Numerical sanity check at the concrete value x = 50.
    lhs = 5 + (500 / 100) * 10
    rhs = (110 / 100) * 50
    passed_num = abs(lhs - rhs) < 1e-12 and abs(rhs - 55) < 1e-12
    if not passed_num:
        proved = False
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(passed_num),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"lhs={lhs}, rhs={rhs}, expected both 55 and equal.",
    })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())