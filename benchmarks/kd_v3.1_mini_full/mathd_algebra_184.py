import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, simplify, sqrt, Rational


# Prove the algebraic characterization using kdrag/Z3.
# Let a and b be positive reals satisfying the geometric-sequence conditions.
# From 6, a, b geometric: a^2 = 6b.
# From 1/b, a, 54 geometric: a^2 = 54/b.
# Hence 6b = 54/b, so b^2 = 9 and positivity gives b = 3.
# Then a^2 = 18 and positivity gives a = 3*sqrt(2).


def verify():
    checks = []
    proved = True

    # --- Check 1: Formal kdrag proof of the key algebraic consequence ---
    # We encode the conclusion as a theorem over positive reals.
    a, b = Reals("a b")
    thm = None
    try:
        thm = kd.prove(
            ForAll(
                [a, b],
                Implies(
                    And(a > 0, b > 0, a * a == 6 * b, a * a == 54 / b),
                    And(b == 3, a * a == 18),
                ),
            )
        )
        checks.append(
            {
                "name": "kdrag_geometric_sequence_algebra",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified theorem proved by kdrag: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "kdrag_geometric_sequence_algebra",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # --- Check 2: SymPy symbolic derivation of b = 3 and a = 3*sqrt(2) ---
    try:
        b_sym = symbols("b", positive=True, real=True)
        sol_b = solve(Eq(6 * b_sym, 54 / b_sym), b_sym)
        ans = simplify(sqrt(6 * sol_b[0])) if sol_b else None
        ok = (sol_b == [3]) and (simplify(ans - 3 * sqrt(2)) == 0)
        if not ok:
            proved = False
        checks.append(
            {
                "name": "sympy_symbolic_solution",
                "passed": bool(ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"solve(Eq(6*b, 54/b), b) -> {sol_b}; derived a -> {ans}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_symbolic_solution",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic check failed: {type(e).__name__}: {e}",
            }
        )

    # --- Check 3: Numerical sanity check at the derived value ---
    try:
        a_val = 3 * 2 ** 0.5
        b_val = 3.0
        left1 = a_val * a_val
        right1 = 6 * b_val
        right2 = 54 / b_val
        ok_num = abs(left1 - right1) < 1e-9 and abs(left1 - right2) < 1e-9
        if not ok_num:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(ok_num),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"a=3*sqrt(2), b=3 gives a^2={left1}, 6b={right1}, 54/b={right2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())