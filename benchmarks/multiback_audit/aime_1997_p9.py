from sympy import symbols, sqrt, Rational, simplify, expand


def verify():
    checks = []

    # --------------------
    # Proof check (SymPy)
    # --------------------
    a = (1 + sqrt(5)) / 2

    # From the condition and 2 < a^2 < 3, we infer floor(a^2)=2 and floor(1/a)=0,
    # hence <a^2> = a^2 - 2 and <a^{-1}> = a^{-1}.
    # The defining relation becomes a^{-1} = a^2 - 2, i.e. a^3 - 2a - 1 = 0.
    proof_poly = simplify(a**3 - 2*a - 1)
    expr = simplify(a**12 - 144/a)
    proof_passed = (proof_poly == 0) and (simplify(expr - 233) == 0)
    checks.append({
        "name": "proof_identity_and_value",
        "passed": bool(proof_passed),
        "check_type": "proof",
        "backend": "sympy",
        "details": f"a^3 - 2a - 1 simplifies to {proof_poly}; target expression simplifies to {simplify(expr)}.",
    })

    # --------------------
    # Sanity check (SymPy)
    # --------------------
    x = symbols('x')
    golden_poly = expand((x + 1)*(x**2 - x - 1))
    sanity_passed = simplify(golden_poly - (x**3 - 2*x - 1)) == 0
    checks.append({
        "name": "sanity_factorization_nontrivial",
        "passed": bool(sanity_passed),
        "check_type": "sanity",
        "backend": "sympy",
        "details": f"(x+1)(x^2-x-1) expands to {golden_poly}, matching x^3-2x-1.",
    })

    # --------------------
    # Numerical check
    # --------------------
    a_num = float((1 + sqrt(5)).evalf() / 2)
    num_val = float((a_num**12) - 144/a_num)
    numerical_passed = abs(num_val - 233.0) < 1e-8
    checks.append({
        "name": "numerical_evaluation",
        "passed": bool(numerical_passed),
        "check_type": "numerical",
        "backend": "numerical",
        "details": f"With a≈{a_num:.12f}, expression≈{num_val:.12f}.",
    })

    return {"checks": checks, "proved": all(c["passed"] for c in checks)}


if __name__ == "__main__":
    result = verify()
    for c in result["checks"]:
        print(f"{c['check_type'].upper()} {c['name']}: {'PASS' if c['passed'] else 'FAIL'} -- {c['details']}")
    print("PROVED:", result["proved"])