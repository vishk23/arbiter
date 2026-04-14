from sympy import Rational, Symbol, cos, sin, pi, simplify, trigsimp, minimal_polynomial, N, tan


def verify():
    checks = []

    # Symbolic/trigonometric proof using exact identities.
    # We verify the derived closed form:
    #   sum_{k=1}^{35} sin(5k degrees) = (1 + cos 5°)/sin 5° = tan(87.5°)
    # and hence m+n = 175+2 = 177.
    x = Symbol('x')
    deg = pi / 180

    # Define the exact sum symbolically.
    s = sum(sin(5 * k * deg) for k in range(1, 36))

    # Check 1: telescoping / closed form identity is symbolically zero.
    # Use the standard product-to-sum identity in exact symbolic form.
    closed_form = (1 + cos(5 * deg)) / sin(5 * deg)
    expr1 = trigsimp(s - closed_form)
    passed1 = simplify(expr1) == 0
    checks.append({
        "name": "telescoping_closed_form",
        "passed": passed1,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Exact symbolic simplification of sum - closed_form gave: {expr1}"
    })

    # Check 2: closed form equals tan(175/2 degrees) exactly.
    target = tan(Rational(175, 2) * deg)
    expr2 = trigsimp(closed_form - target)
    passed2 = simplify(expr2) == 0
    checks.append({
        "name": "closed_form_equals_tan_175_over_2",
        "passed": passed2,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Exact symbolic simplification of closed_form - tan(175/2°) gave: {expr2}"
    })

    # Check 3: numerical sanity check at high precision.
    s_num = N(s, 50)
    t_num = N(target, 50)
    passed3 = abs(s_num - t_num) < Rational(1, 10**20)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(passed3),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"N(sum)={s_num}, N(tan(175/2°))={t_num}"
    })

    # Final conclusion: if the exact symbolic checks pass, m = 175 and n = 2, so m+n=177.
    proved = all(c["passed"] for c in checks)
    checks.append({
        "name": "final_answer_m_plus_n",
        "passed": proved,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "From the exact identity sum = tan(175/2°), we infer m=175, n=2, hence m+n=177."
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)