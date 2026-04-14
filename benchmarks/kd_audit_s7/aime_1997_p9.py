from sympy import Symbol, Rational, sqrt, simplify, minimal_polynomial


def verify():
    checks = []
    proved = True

    # Check 1: From 2 < a^2 < 3 and a > 0, we have 0 < a < sqrt(3) < 2,
    # so 0 < a^{-1} and <a^{-1}> = a^{-1}. Also <a^2> = a^2 - 2.
    # Hence a^{-1} = a^2 - 2, or a^3 - 2a - 1 = 0.
    try:
        a = Symbol('a', positive=True, real=True)
        expr = a**3 - 2*a - 1
        factored = simplify(expr - (a + 1)*(a**2 - a - 1))
        passed = (factored == 0)
        checks.append({
            "name": "cubic_factorization",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "Verified that a^3 - 2a - 1 = (a + 1)(a^2 - a - 1)."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "cubic_factorization",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification failed: {e}"
        })
        proved = False

    # Check 2: The positive root of a^2 - a - 1 = 0 is the golden ratio.
    try:
        x = Symbol('x')
        phi = (1 + sqrt(5)) / 2
        mp = minimal_polynomial(phi, x)
        passed = (mp == x**2 - x - 1)
        checks.append({
            "name": "phi_minimal_polynomial",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(phi, x) = {mp}, matching x^2 - x - 1."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "phi_minimal_polynomial",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification failed: {e}"
        })
        proved = False

    # Check 3: Evaluate the target expression exactly.
    try:
        phi = (1 + sqrt(5)) / 2
        target = simplify(phi**12 - 144/phi)
        passed = simplify(target - 233) == 0
        checks.append({
            "name": "target_value",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed a^12 - 144/a = {target}, expected 233."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "target_value",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification failed: {e}"
        })
        proved = False

    return {"proved": proved, "checks": checks}