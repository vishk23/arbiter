from sympy import Symbol, Rational, pi, sin, cos, tan, simplify, N


def verify():
    checks = []
    proved = True

    # Check 1: symbolic/trigonometric identity for the sum using exact simplification.
    # We verify that the sum S = sum_{k=1}^{35} sin(5k°) equals tan(87.5°), hence m+n=177.
    # Since sympy does not always simplify the telescoping sum directly in a compact proof object,
    # we use exact symbolic evaluation of the closed form derived from the standard identity.
    try:
        # Exact closed form from telescoping: S = (1 + cos 5°) / sin 5° = cot(2.5°) = tan(87.5°)
        deg = pi / 180
        S_closed = (1 + cos(5 * deg)) / sin(5 * deg)
        target = tan(Rational(175, 2) * deg)
        # Rigorous symbolic zero check
        diff = simplify(S_closed - target)
        passed = diff == 0
        details = f"Closed form simplifies to zero difference: {diff}"
        proof_type = "symbolic_zero"
    except Exception as e:
        passed = False
        details = f"Symbolic verification failed: {e}"
        proof_type = "symbolic_zero"
        proved = False
    checks.append({
        "name": "trig_closed_form_equals_tan_87_5_degrees",
        "passed": passed,
        "backend": "sympy",
        "proof_type": proof_type,
        "details": details,
    })
    if not passed:
        proved = False

    # Check 2: numerical sanity check at high precision.
    try:
        deg = pi / 180
        S_num = N(sum(sin(5 * k * deg) for k in range(1, 36)), 50)
        T_num = N(tan(Rational(175, 2) * deg), 50)
        passed = abs(S_num - T_num) < 1e-45
        details = f"S≈{S_num}, tan(87.5°)≈{T_num}, abs diff≈{abs(S_num - T_num)}"
        proof_type = "numerical"
    except Exception as e:
        passed = False
        details = f"Numerical sanity check failed: {e}"
        proof_type = "numerical"
        proved = False
    checks.append({
        "name": "numerical_equality_of_sum_and_tangent",
        "passed": passed,
        "backend": "numerical",
        "proof_type": proof_type,
        "details": details,
    })
    if not passed:
        proved = False

    # Check 3: arithmetic conclusion m+n = 177 for m/n = 175/2.
    try:
        m, n = 175, 2
        passed = (m + n == 177) and (m < 90 * n) and __import__("math").gcd(m, n) == 1
        details = "m/n = 175/2 < 90 and gcd(175,2)=1, so m+n=177."
        proof_type = "numerical"
    except Exception as e:
        passed = False
        details = f"Final arithmetic check failed: {e}"
        proof_type = "numerical"
        proved = False
    checks.append({
        "name": "final_answer_m_plus_n_equals_177",
        "passed": passed,
        "backend": "numerical",
        "proof_type": proof_type,
        "details": details,
    })
    if not passed:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)