from sympy import symbols, sin, cos, tan, simplify, pi, N, Rational, trigsimp


def verify():
    checks = []

    # Problem statement: s = sum_{k=1}^{35} sin(5k degrees)
    # Claim: s = tan(175/2 degrees), so m+n = 175+2 = 177.

    # PROOF check (symbolic trigonometric verification)
    # Use the telescoping identity derived from product-to-sum:
    # s*sin(5°) = (1 + cos 5°)/2
    # Therefore s = (1 + cos 5°)/(2 sin 5°) = tan(87.5°) = tan(175/2°)
    deg = pi / 180
    expr = (1 + cos(5 * deg)) / (2 * sin(5 * deg)) - tan(Rational(175, 2) * deg)
    proof_simplified = trigsimp(simplify(expr))
    proof_passed = simplify(proof_simplified) == 0
    checks.append({
        "name": "proof_trig_identity",
        "passed": bool(proof_passed),
        "check_type": "proof",
        "backend": "sympy",
        "details": f"Simplified difference: {proof_simplified}"
    })

    # SANITY check: confirm the sum is non-trivial and the telescoping form is meaningful
    s_sanity = sum(sin(5 * k * deg) for k in range(1, 36))
    telescoping_rhs = (1 + cos(5 * deg)) / (2 * sin(5 * deg))
    sanity_passed = simplify(telescoping_rhs) != 0 and s_sanity != 0
    checks.append({
        "name": "sanity_nontrivial_sum",
        "passed": bool(sanity_passed),
        "check_type": "sanity",
        "backend": "sympy",
        "details": f"sum expression nonzero: {s_sanity != 0}, rhs nonzero: {telescoping_rhs != 0}"
    })

    # NUMERICAL check: evaluate both sides numerically and compare
    numeric_sum = N(sum(sin(5 * k * deg) for k in range(1, 36)), 20)
    numeric_tan = N(tan(Rational(175, 2) * deg), 20)
    numeric_passed = abs(float(numeric_sum - numeric_tan)) < 1e-10
    checks.append({
        "name": "numerical_evaluation",
        "passed": bool(numeric_passed),
        "check_type": "numerical",
        "backend": "numerical",
        "details": f"sum≈{numeric_sum}, tan(175/2)≈{numeric_tan}"
    })

    return {"checks": checks, "passed": all(c["passed"] for c in checks)}


if __name__ == "__main__":
    result = verify()
    print(result)