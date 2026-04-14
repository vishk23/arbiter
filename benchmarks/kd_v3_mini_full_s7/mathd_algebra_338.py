import sympy as sp
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof using kdrag.
    try:
        a, b, c = Real("a"), Real("b"), Real("c")
        # From the linear system, derive the unique solution and the product.
        # This is Z3-encodable and yields a certificate if the theorem is valid.
        thm = kd.prove(
            ForAll(
                [a, b, c],
                Implies(
                    And(
                        3 * a + b + c == -3,
                        a + 3 * b + c == 9,
                        a + b + 3 * c == 19,
                    ),
                    a * b * c == -56,
                ),
            )
        )
        checks.append(
            {
                "name": "kdrag_linear_system_product",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned certificate: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "kdrag_linear_system_product",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Symbolic solve with SymPy and exact multiplication.
    try:
        a, b, c = sp.symbols("a b c")
        sol = sp.solve(
            [sp.Eq(3 * a + b + c, -3), sp.Eq(a + 3 * b + c, 9), sp.Eq(a + b + 3 * c, 19)],
            [a, b, c],
            dict=True,
        )[0]
        abc = sp.simplify(sol[a] * sol[b] * sol[c])
        passed = sp.simplify(abc - (-56)) == 0
        if not passed:
            proved = False
        checks.append(
            {
                "name": "sympy_solve_and_multiply",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Solution = {sol}; abc = {abc}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sympy_solve_and_multiply",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Symbolic check failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Numerical sanity check at the concrete solution a=-4, b=2, c=7.
    try:
        a0, b0, c0 = -4, 2, 7
        eq1 = 3 * a0 + b0 + c0
        eq2 = a0 + 3 * b0 + c0
        eq3 = a0 + b0 + 3 * c0
        abc0 = a0 * b0 * c0
        passed = (eq1 == -3) and (eq2 == 9) and (eq3 == 19) and (abc0 == -56)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Evaluated equations to ({eq1}, {eq2}, {eq3}); abc = {abc0}",
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
    import json
    print(json.dumps(verify(), indent=2, sort_keys=True))