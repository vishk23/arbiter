import sympy as sp


def verify():
    checks = []

    # Check 1: rigorous symbolic proof that the interpolating quadratic through
    # the three given values evaluates to 334 at the target point.
    try:
        k = sp.Symbol('k')
        x = sp.Symbol('x')
        poly = sp.interpolate([(1, 1), (2, 12), (3, 123)], k)
        target_expr = sp.expand(poly.subs(k, 4) - 334)
        mp = sp.minimal_polynomial(target_expr, x)
        passed = (sp.expand(mp) == x)
        checks.append({
            "name": "sympy_interpolation_target_value",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Interpolated polynomial is {sp.expand(poly)}; minimal_polynomial((f(4)-334)) = {mp}."
        })
    except Exception as e:
        checks.append({
            "name": "sympy_interpolation_target_value",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic proof failed: {e}"
        })

    # Check 2: verified kdrag/Z3 proof that any quadratic matching the three
    # given values must satisfy f(4)=334.
    try:
        import kdrag as kd
        from kdrag.smt import Real, ForAll, Implies

        a = Real("a")
        b = Real("b")
        c = Real("c")

        theorem = ForAll(
            [a, b, c],
            Implies(
                (a + b + c == 1) & (4*a + 2*b + c == 12) & (9*a + 3*b + c == 123),
                16*a + 4*b + c == 334
            )
        )
        pf = kd.prove(theorem)
        checks.append({
            "name": "kdrag_quadratic_determines_f4",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proved theorem: {pf}"
        })
    except Exception as e:
        checks.append({
            "name": "kdrag_quadratic_determines_f4",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}"
        })

    # Check 3: rigorous symbolic verification of the finite-difference identity
    # for quadratics: f(4) = 3 f(3) - 3 f(2) + f(1).
    try:
        a, b, c = sp.symbols('a b c')
        expr = (a*4**2 + b*4 + c) - (3*(a*3**2 + b*3 + c) - 3*(a*2**2 + b*2 + c) + (a*1**2 + b*1 + c))
        expr = sp.expand(expr)
        x = sp.Symbol('x')
        mp = sp.minimal_polynomial(expr, x)
        passed = (sp.expand(mp) == x)
        checks.append({
            "name": "sympy_quadratic_finite_difference_identity",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Expanded identity difference is {expr}; minimal_polynomial = {mp}."
        })
    except Exception as e:
        checks.append({
            "name": "sympy_quadratic_finite_difference_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy identity proof failed: {e}"
        })

    # Check 4: numerical sanity check using the derived quadratic.
    try:
        k = sp.Symbol('k')
        poly = sp.expand(sp.interpolate([(1, 1), (2, 12), (3, 123)], k))
        val = sp.N(poly.subs(k, 4), 50)
        passed = (sp.Integer(poly.subs(k, 4)) == 334)
        checks.append({
            "name": "numerical_sanity_interpolated_value",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Interpolated polynomial {poly} gives f(4) = {val}."
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_interpolated_value",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}"
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)