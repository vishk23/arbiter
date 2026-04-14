import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve, Integer


def verify() -> dict:
    checks = []
    proved = True

    # Certified proof: solve the linear system in Z3 and prove the larger number is 18.
    x = Real("x")
    y = Real("y")
    try:
        thm = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(x + y == 25, x - y == 11),
                    And(x == 18, x > y),
                ),
            )
        )
        checks.append(
            {
                "name": "kdrag_linear_system_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "kdrag_linear_system_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # SymPy symbolic verification of the same linear system.
    try:
        xs, ys = symbols("x y")
        sol = solve([Eq(xs + ys, 25), Eq(xs - ys, 11)], [xs, ys], dict=True)
        sympy_passed = len(sol) == 1 and sol[0][xs] == Integer(18)
        if not sympy_passed:
            proved = False
        checks.append(
            {
                "name": "sympy_solve_system",
                "passed": sympy_passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"solve(...) returned {sol}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_solve_system",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy solve failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete solution x=18, y=7.
    try:
        x0, y0 = 18, 7
        numerical_passed = (x0 + y0 == 25) and (x0 - y0 == 11) and (x0 > y0)
        if not numerical_passed:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": numerical_passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Checked x={x0}, y={y0}: sum={x0+y0}, diff={x0-y0}, larger={x0}",
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