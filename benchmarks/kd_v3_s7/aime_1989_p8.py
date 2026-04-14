import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: symbolic verification by solving the linear system and evaluating the target.
    try:
        x = sp.symbols('x1:8', real=True)
        A = sp.Matrix([
            [1, 4, 9, 16, 25, 36, 49],
            [4, 9, 16, 25, 36, 49, 64],
            [9, 16, 25, 36, 49, 64, 81],
        ])
        b = sp.Matrix([1, 12, 123])
        target_coeffs = sp.Matrix([16, 25, 36, 49, 64, 81, 100])
        sol = sp.linsolve((A, b), x)
        passed = False
        details = ""
        if sol:
            sol_tuple = next(iter(sol))
            target_expr = sp.simplify(sum(target_coeffs[i] * sol_tuple[i] for i in range(7)))
            passed = sp.simplify(target_expr - 334) == 0
            details = f"linsolve found a parametric solution; target simplifies to {sp.simplify(target_expr)}."
        else:
            details = "SymPy linsolve returned no solution set."
        checks.append({
            "name": "symbolic_linear_system_target",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": details,
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "symbolic_linear_system_target",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed with exception: {e}",
        })
        proved = False

    # Check 2: verified algebraic certificate via finite-difference linearity.
    # For f(k)=sum_{i=1}^7 (k+i-1)^2 x_i, f is quadratic in k.
    # Thus f(4) is determined from f(1), f(2), f(3) by quadratic interpolation.
    try:
        k = sp.Symbol('k')
        f1, f2, f3 = sp.Integer(1), sp.Integer(12), sp.Integer(123)
        a, bcoef, c = sp.symbols('a b c')
        sol_abc = sp.solve(
            [sp.Eq(a + bcoef + c, f1), sp.Eq(4*a + 2*bcoef + c, f2), sp.Eq(9*a + 3*bcoef + c, f3)],
            [a, bcoef, c], dict=True
        )
        passed = False
        details = ""
        if sol_abc:
            s = sol_abc[0]
            f4 = sp.simplify(16*s[a] + 4*s[bcoef] + s[c])
            passed = sp.simplify(f4 - 334) == 0
            details = f"Quadratic interpolation gives a={s[a]}, b={s[bcoef]}, c={s[c]}, hence f(4)={f4}."
        else:
            details = "No solution found for quadratic interpolation system."
        checks.append({
            "name": "quadratic_interpolation_certificate",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": details,
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "quadratic_interpolation_certificate",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Quadratic interpolation verification failed with exception: {e}",
        })
        proved = False

    # Check 3: numerical sanity check using an explicit satisfying assignment.
    # One convenient solution is x1=0,x2=0,x3=0,x4=0,x5=0,x6=0,x7=1/49?  No, we instead use a direct
    # least-squares/parametric solution from SymPy and check the target numerically.
    try:
        x = sp.symbols('x1:8', real=True)
        A = sp.Matrix([
            [1, 4, 9, 16, 25, 36, 49],
            [4, 9, 16, 25, 36, 49, 64],
            [9, 16, 25, 36, 49, 64, 81],
        ])
        b = sp.Matrix([1, 12, 123])
        sol = sp.linsolve((A, b), x)
        passed = False
        details = ""
        if sol:
            sol_tuple = next(iter(sol))
            # Pick a concrete parameter value t=0 for the free symbols.
            free_syms = sorted(list(sol_tuple.free_symbols), key=lambda s: s.name)
            subs_map = {s: 0 for s in free_syms}
            concrete = [sp.N(expr.subs(subs_map)) for expr in sol_tuple]
            lhs_vals = [sp.N(sum(A[i, j] * concrete[j] for j in range(7))) for i in range(3)]
            target = sp.N(sum([16, 25, 36, 49, 64, 81, 100][j] * concrete[j] for j in range(7)))
            passed = all(sp.simplify(lhs_vals[i] - b[i]) == 0 for i in range(3)) and sp.simplify(target - 334) == 0
            details = f"Concrete parameter choice verifies the three equations and yields target {target}."
        else:
            details = "No parametric solution available for numerical sanity check."
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details,
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed with exception: {e}",
        })
        proved = False

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, sort_keys=True))