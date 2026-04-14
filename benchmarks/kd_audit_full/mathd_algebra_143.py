from sympy import Symbol, simplify


def verify():
    checks = []
    proved_all = True

    # Checked claim: g(2) = 7 and f(g(2)) = 8 for f(x)=x+1, g(x)=x^2+3.
    try:
        x = Symbol('x')
        f = lambda t: t + 1
        g = lambda t: t**2 + 3

        g2 = simplify(g(2))
        fg2 = simplify(f(g2))
        passed = (g2 == 7) and (fg2 == 8)
        checks.append({
            "name": "compute_g2_and_f_g2",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"g(2) simplifies to {g2}; f(g(2)) simplifies to {fg2}."
        })
        proved_all = proved_all and passed
    except Exception as e:
        checks.append({
            "name": "compute_g2_and_f_g2",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy evaluation failed: {e}"
        })
        proved_all = False

    # Numerical sanity check at the concrete value 2.
    try:
        f_num = lambda t: t + 1
        g_num = lambda t: t**2 + 3
        passed = (f_num(g_num(2)) == 8)
        checks.append({
            "name": "numerical_sanity_f_of_g_of_2",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Direct evaluation gives f(g(2)) = {f_num(g_num(2))}."
        })
        proved_all = proved_all and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_f_of_g_of_2",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}"
        })
        proved_all = False

    # A small verified algebraic check using SymPy exact simplification.
    try:
        x = Symbol('x')
        expr = (x + 1).subs(x, (x**2 + 3)).subs(x, 2)
        passed = simplify(expr) == 8
        checks.append({
            "name": "symbolic_substitution_check",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exact substitution simplifies to {simplify(expr)}."
        })
        proved_all = proved_all and passed
    except Exception as e:
        checks.append({
            "name": "symbolic_substitution_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic substitution failed: {e}"
        })
        proved_all = False

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)