from typing import Any, Dict, List


def verify() -> dict:
    checks: List[Dict[str, Any]] = []

    # Verified proof with Knuckledragger / Z3
    try:
        import kdrag as kd
        from kdrag.smt import Real, ForAll, Implies, And

        a = Real("a")
        b = Real("b")
        c = Real("c")

        thm = ForAll(
            [a, b, c],
            Implies(
                And(
                    a + b + c == 1,
                    4 * a + 2 * b + c == 12,
                    9 * a + 3 * b + c == 123,
                ),
                16 * a + 4 * b + c == 334,
            ),
        )
        proof = kd.prove(thm)
        checks.append(
            {
                "name": "quadratic_interpolation_implies_f4_334",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(proof),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "quadratic_interpolation_implies_f4_334",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Knuckledragger proof failed: {type(e).__name__}: {e}",
            }
        )

    # Symbolic algebra check: the weighted sum is always a quadratic in k, so f(4) is determined
    try:
        import sympy as sp

        x = sp.symbols('x1:8', real=True)
        k = sp.symbols('k', real=True)
        f = sum((k + i) ** 2 * x[i] for i in range(7))
        f_expanded = sp.expand(f)
        poly = sp.Poly(f_expanded, k)
        deg_ok = poly.degree() <= 2

        y = sp.symbols('y')
        expr = sp.expand((16 * 50 + 4 * (-139) + 90) - 334)
        mp = sp.minimal_polynomial(expr, y)
        passed = deg_ok and (mp == y)
        checks.append(
            {
                "name": "symbolic_quadratic_form_and_constant_evaluation",
                "passed": bool(passed),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"degree_in_k={poly.degree()}, minimal_polynomial_of((16*50+4*(-139)+90)-334)={mp}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "symbolic_quadratic_form_and_constant_evaluation",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check using one concrete solution of the 3x7 system
    try:
        import sympy as sp

        x1, x2, x3, x4, x5, x6, x7 = sp.symbols('x1 x2 x3 x4 x5 x6 x7', real=True)
        eqs = [
            sp.Eq(1*x1 + 4*x2 + 9*x3 + 16*x4 + 25*x5 + 36*x6 + 49*x7, 1),
            sp.Eq(4*x1 + 9*x2 + 16*x3 + 25*x4 + 36*x5 + 49*x6 + 64*x7, 12),
            sp.Eq(9*x1 + 16*x2 + 25*x3 + 36*x4 + 49*x5 + 64*x6 + 81*x7, 123),
            sp.Eq(x4, 0),
            sp.Eq(x5, 0),
            sp.Eq(x6, 0),
            sp.Eq(x7, 0),
        ]
        sol = sp.solve(eqs, [x1, x2, x3, x4, x5, x6, x7], dict=True)
        if not sol:
            raise ValueError("No concrete solution found for sanity check")
        s = sol[0]
        target = sp.expand(16*s[x1] + 25*s[x2] + 36*s[x3] + 49*s[x4] + 64*s[x5] + 81*s[x6] + 100*s[x7])
        passed = sp.simplify(target - 334) == 0
        checks.append(
            {
                "name": "numerical_sanity_concrete_solution",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Concrete solution with x4=x5=x6=x7=0 gives target={target}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_concrete_solution",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, sort_keys=True))