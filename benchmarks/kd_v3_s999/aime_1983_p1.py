import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, simplify, Rational


def verify():
    checks = []
    proved_all = True

    # ---------------------------------
    # Verified proof in kdrag/Z3
    # ---------------------------------
    try:
        A = Real("A")
        p = Real("p")
        q = Real("q")
        r = Real("r")

        thm = kd.prove(
            ForAll(
                [A, p, q, r],
                Implies(
                    And(
                        A > 0,
                        p > 0,
                        q > 0,
                        r > 0,
                        A / p == 24,
                        A / q == 40,
                        A / (p + q + r) == 12,
                    ),
                    A / r == 60,
                ),
            )
        )
        checks.append(
            {
                "name": "kdrag_proof_log_value",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "kdrag_proof_log_value",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # ---------------------------------
    # SymPy symbolic derivation check
    # ---------------------------------
    try:
        A = symbols('A', positive=True)
        p, q, r = symbols('p q r', positive=True)
        p_expr = A / 24
        q_expr = A / 40
        r_expr = A / 12 - p_expr - q_expr
        derived = simplify(A / r_expr)
        passed = simplify(derived - 60) == 0
        if not passed:
            proved_all = False
        checks.append(
            {
                "name": "sympy_symbolic_derivation",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Derived A/r simplifies to {derived}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "sympy_symbolic_derivation",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic check failed: {type(e).__name__}: {e}",
            }
        )

    # ---------------------------------
    # Numerical sanity check
    # Choose a concrete consistent instance: w=2^120, x=2^5, y=2^3, z=2^2
    # Then log_x w = 120/5 = 24, log_y w = 120/3 = 40, log_{xyz} w = 120/10 = 12.
    # ---------------------------------
    try:
        w = 2.0 ** 120
        x = 2.0 ** 5
        y = 2.0 ** 3
        z = 2.0 ** 2
        import math
        c1 = abs(math.log(w, x) - 24.0) < 1e-9
        c2 = abs(math.log(w, y) - 40.0) < 1e-9
        c3 = abs(math.log(w, x * y * z) - 12.0) < 1e-9
        c4 = abs(math.log(w, z) - 60.0) < 1e-9
        passed = c1 and c2 and c3 and c4
        if not passed:
            proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_instance",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Checked a concrete instance x=2^5, y=2^3, z=2^2, w=2^120 gives logs 24, 40, 12, 60.",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_instance",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    print(verify())