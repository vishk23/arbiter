from sympy import symbols, cos, sin, pi, simplify, N


def verify():
    checks = []

    # Proof check: symbolic trigonometric simplification
    x = pi / 7
    lhs = cos(x) - cos(2 * x) + cos(3 * x)
    target = simplify(1 / 2)
    expr = simplify(lhs - target)
    proof_passed = expr == 0
    checks.append({
        "name": "proof_trig_identity",
        "passed": bool(proof_passed),
        "check_type": "proof",
        "backend": "sympy",
        "details": f"simplify(lhs - 1/2) -> {expr}"
    })

    # Sanity check: the expression is non-trivial and the transformed sum is well-formed
    transformed = cos(x) + cos(3 * x) + cos(5 * x)
    sanity_passed = simplify(lhs - transformed) == 0 and simplify(transformed) != 0
    checks.append({
        "name": "sanity_transformation_equivalence",
        "passed": bool(sanity_passed),
        "check_type": "sanity",
        "backend": "sympy",
        "details": f"lhs and transformed sum are symbolically equivalent; transformed -> {simplify(transformed)}"
    })

    # Numerical check: evaluate at a concrete numeric approximation
    numeric_val = N(lhs)
    numeric_target = N(1 / 2)
    numerical_passed = abs(float(numeric_val - numeric_target)) < 1e-12
    checks.append({
        "name": "numerical_evaluation",
        "passed": bool(numerical_passed),
        "check_type": "numerical",
        "backend": "numerical",
        "details": f"lhs ≈ {numeric_val}, target ≈ {numeric_target}"
    })

    return {
        "proved": all(c["passed"] for c in checks),
        "checks": checks,
    }


if __name__ == "__main__":
    result = verify()
    for c in result["checks"]:
        print(f"{c['name']}: {c['passed']} ({c['check_type']}, {c['backend']}) - {c['details']}")
    print("PROVED" if result["proved"] else "NOT PROVED")