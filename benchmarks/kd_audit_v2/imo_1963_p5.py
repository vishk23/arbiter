from sympy import Symbol, cos, pi, Rational, minimal_polynomial, simplify, N


def verify():
    checks = []
    proved = True

    # Verified symbolic proof using algebraic-number certificate.
    # We certify that the exact expression equals 1/2 by showing the
    # algebraic expression E - 1/2 is identically zero.
    x = Symbol('x')
    expr = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7)
    zero_expr = simplify(expr - Rational(1, 2))
    try:
        mp = minimal_polynomial(zero_expr, x)
        passed = (mp == x)
        details = f"minimal_polynomial(expr - 1/2, x) = {mp}; expected x"
    except Exception as e:
        passed = False
        details = f"SymPy minimal_polynomial failed: {e}"
    checks.append({
        "name": "symbolic_trig_identity",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    })
    proved = proved and passed

    # Numerical sanity check at high precision.
    try:
        val = N(expr, 50)
        target = N(Rational(1, 2), 50)
        diff = abs(val - target)
        passed = diff < 1e-45
        details = f"value={val}; target={target}; |diff|={diff}"
    except Exception as e:
        passed = False
        details = f"Numerical evaluation failed: {e}"
    checks.append({
        "name": "numerical_sanity_check",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": details,
    })
    proved = proved and passed

    # Additional symbolic check mirroring the classical product-sum rewrite.
    # This is not the main certificate, but it confirms the equivalent form.
    try:
        rewritten = simplify(cos(pi/7) + cos(3*pi/7) + cos(5*pi/7) - expr)
        passed = (rewritten == 0)
        details = f"Equivalent cosine-sum rewrite simplifies to {rewritten}"
    except Exception as e:
        passed = False
        details = f"Rewrite verification failed: {e}"
    checks.append({
        "name": "equivalent_cosine_rewrite",
        "passed": passed,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details,
    })
    proved = proved and passed

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)