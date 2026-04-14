from sympy import Integer, Rational, simplify, sqrt, root


def verify():
    checks = []

    # Verified symbolic/algebraic proof of the exact value.
    expr = sqrt(Integer(1000000)) - Integer(1000000) ** Rational(1, 3)
    symbolic_value = simplify(expr)
    symbolic_passed = symbolic_value == Integer(900)
    checks.append({
        "name": "symbolic_exact_value",
        "passed": bool(symbolic_passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"simplify(sqrt(1000000) - 1000000**(1/3)) -> {symbolic_value}",
    })

    # Numerical sanity check at a concrete value.
    numeric_expr = float(sqrt(1000000)) - float(1000000 ** (1 / 3))
    numeric_passed = abs(numeric_expr - 900.0) < 1e-9
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(numeric_passed),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"float evaluation gives {numeric_expr}",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)