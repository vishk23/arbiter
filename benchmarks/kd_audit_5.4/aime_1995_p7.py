from sympy import symbols, Rational, sqrt, simplify, minimal_polynomial, N


def verify():
    checks = []

    # Symbolic variables for exact algebraic manipulation
    s = symbols('s')
    x = symbols('x')

    # Let s = sin(t) + cos(t). From (1+sin t)(1+cos t)=5/4 and sin^2+cos^2=1,
    # we derive s^2 + 2s - 3/2 = 0, hence s = -1 ± sqrt(5/2).
    expr_quadratic = (sqrt(10)/2 - 1)**2 + 2*(sqrt(10)/2 - 1) - Rational(3, 2)
    try:
        mp1 = minimal_polynomial(simplify(expr_quadratic), x)
        passed1 = (mp1 == x)
        details1 = (
            "Verified symbolically that s = sqrt(10)/2 - 1 satisfies "
            "s^2 + 2s - 3/2 = 0 by proving the residual has minimal polynomial x."
        )
    except Exception as e:
        passed1 = False
        details1 = f"SymPy symbolic proof failed: {e}"
    checks.append({
        "name": "candidate_sum_satisfies_quadratic",
        "passed": passed1,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details1,
    })

    # The other root is -1 - sqrt(5/2), whose magnitude exceeds sqrt(2),
    # so it cannot equal sin t + cos t. Numerically sanity-check this.
    other_root = -1 - sqrt(10)/2
    passed2 = abs(float(N(other_root, 50))) > float(N(sqrt(2), 50))
    checks.append({
        "name": "reject_other_root_by_bound",
        "passed": passed2,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Numerically checked |-1 - sqrt(10)/2| > sqrt(2), so this root cannot be sin t + cos t.",
    })

    # Using 2ab + 2(a+b) = 1/2, we get ab = 1/4 - (a+b).
    # Then (1-a)(1-b) = 1 - (a+b) + ab = 5/4 - 2(a+b).
    # Substitute a+b = sqrt(10)/2 - 1 to get 13/4 - sqrt(10).
    target_expr = simplify(Rational(5, 4) - 2*(sqrt(10)/2 - 1) - (Rational(13, 4) - sqrt(10)))
    try:
        mp3 = minimal_polynomial(target_expr, x)
        passed3 = (mp3 == x)
        details3 = (
            "Verified symbolically that (1-sin t)(1-cos t) equals 13/4 - sqrt(10) "
            "after substituting sin t + cos t = sqrt(10)/2 - 1."
        )
    except Exception as e:
        passed3 = False
        details3 = f"SymPy symbolic proof failed: {e}"
    checks.append({
        "name": "final_expression_matches",
        "passed": passed3,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": details3,
    })

    # Numerical sanity check with a concrete solution reconstructed from sum/product.
    # If u = sin t + cos t and v = sin t cos t = 1/4 - u, then sin and cos are roots of z^2 - uz + v.
    u = sqrt(10)/2 - 1
    v = Rational(1, 4) - u
    disc = simplify(u**2 - 4*v)
    sin_val = simplify((u + sqrt(disc)) / 2)
    cos_val = simplify((u - sqrt(disc)) / 2)
    lhs_num = N((1 + sin_val)*(1 + cos_val), 50)
    rhs_num = N((1 - sin_val)*(1 - cos_val), 50)
    passed4 = abs(float(lhs_num - N(Rational(5, 4), 50))) < 1e-12 and abs(float(rhs_num - N(Rational(13, 4) - sqrt(10), 50))) < 1e-12
    checks.append({
        "name": "numerical_sanity_concrete_solution",
        "passed": passed4,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Constructed exact sin t, cos t from the derived sum/product and numerically checked both given and final products.",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)