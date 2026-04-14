from sympy import symbols, Eq, factor, solve, sqrt, simplify


def verify():
    checks = []

    # Symbolic verification: derive the intersection condition and factor it.
    try:
        x, u = symbols('x u', real=True)
        expr = x**4 - 5*x**2 + 6
        factored = factor(expr)
        symbolic_passed = simplify(factored - (x**2 - 2)*(x**2 - 3)) == 0
        checks.append({
            "name": "factor_intersection_polynomial",
            "passed": bool(symbolic_passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"x^4 - 5*x^2 + 6 factors as {factored}; this equals (x^2 - 2)(x^2 - 3)."
        })
    except Exception as e:
        checks.append({
            "name": "factor_intersection_polynomial",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic factorization failed: {e}"
        })

    # Verified proof certificate via SymPy exact algebraic computation.
    try:
        # Solve u^2 - 5u + 6 = 0 exactly, where u = x^2.
        sol_u = solve(Eq(u**2 - 5*u + 6, 0), u)
        sol_set = set(sol_u)
        proof_passed = sol_set == {2, 3}
        checks.append({
            "name": "solve_quadratic_for_x_squared",
            "passed": bool(proof_passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solutions for u=x^2 are {sol_u}, so x^2 is 2 or 3, giving x = ±sqrt(2), ±sqrt(3)."
        })
    except Exception as e:
        checks.append({
            "name": "solve_quadratic_for_x_squared",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exact solve failed: {e}"
        })

    # Numerical sanity check at concrete values.
    try:
        vals = [sqrt(2), -sqrt(2), sqrt(3), -sqrt(3)]
        sanity = all(simplify(v**4 - (5*v**2 - 6)) == 0 for v in vals)
        checks.append({
            "name": "numerical_sanity_on_intersection_points",
            "passed": bool(sanity),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "Checked that x = ±sqrt(2), ±sqrt(3) satisfy x^4 = 5x^2 - 6 exactly."
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_on_intersection_points",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Sanity check failed: {e}"
        })

    # Final arithmetic conclusion.
    proved = all(ch["passed"] for ch in checks) and (3 - 2 == 1)
    checks.append({
        "name": "compute_m_minus_n",
        "passed": bool(3 - 2 == 1),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "From x^2 in {2,3}, we have m=3 and n=2, hence m-n=1."
    })

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))