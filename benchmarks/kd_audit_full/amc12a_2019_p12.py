from sympy import symbols, Eq, solve, Rational, sqrt, simplify

try:
    import kdrag as kd
    from kdrag.smt import Real, ForAll, Implies, And, Not
    KDRAG_AVAILABLE = True
except Exception:
    KDRAG_AVAILABLE = False


def verify():
    checks = []
    proved = True

    # Verified symbolic proof using SymPy algebra.
    try:
        k = symbols('k', real=True)
        expr = (k - Rational(4, 1) / k) ** 2
        # From k + 4/k = 6, derive k^2 - 6k + 4 = 0, hence k = 3 ± sqrt(5)
        sols = solve(Eq(k**2 - 6*k + 4, 0), k)
        val_set = set()
        for s in sols:
            val_set.add(simplify(expr.subs(k, s)))
        sympy_passed = (val_set == {Rational(20, 1)})
        checks.append({
            "name": "symbolic_derivation_of_square",
            "passed": bool(sympy_passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Solved k^2 - 6k + 4 = 0 with solutions {sols}; substituted into (k - 4/k)^2 giving {val_set}."
        })
        proved = proved and bool(sympy_passed)
    except Exception as e:
        checks.append({
            "name": "symbolic_derivation_of_square",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic proof failed: {e}"
        })
        proved = False

    # Numerical sanity check at one root.
    try:
        k_val = 3 + sqrt(5)
        num_expr = simplify((k_val - 4 / k_val) ** 2)
        num_passed = simplify(num_expr - 20) == 0
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(num_passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Evaluated at k = 3 + sqrt(5): (k - 4/k)^2 = {num_expr}."
        })
        proved = proved and bool(num_passed)
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}"
        })
        proved = False

    # Optional kdrag certificate check for a derived linear identity.
    if KDRAG_AVAILABLE:
        try:
            k = Real('k')
            thm = kd.prove(ForAll([k], Implies(k*k - 6*k + 4 == 0, (k - 4/k)**2 == 20)))
            checks.append({
                "name": "kdrag_certificate_check",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag produced proof object: {thm}."
            })
        except Exception as e:
            checks.append({
                "name": "kdrag_certificate_check",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof could not be constructed: {e}"
            })
            proved = False
    else:
        checks.append({
            "name": "kdrag_certificate_check",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag not available in this environment."
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)