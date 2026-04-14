from sympy import Integer, Rational, simplify, sqrt


def verify():
    checks = []
    proved = True

    # Verified symbolic check: exact arithmetic in SymPy.
    expr = sqrt(Integer(1000000)) - Integer(1000000) ** Rational(1, 3)
    simplified = simplify(expr)
    symbolic_passed = simplified == Integer(900)
    checks.append(
        {
            "name": "symbolic_evaluation_of_sqrt_and_cuberoot",
            "passed": bool(symbolic_passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"simplify(sqrt(1000000) - 1000000**(1/3)) -> {simplified!r}; expected 900.",
        }
    )

    # Numerical sanity check at the concrete value.
    numeric_val = float(sqrt(1000000)) - float(1000000 ** (1 / 3))
    numerical_passed = abs(numeric_val - 900.0) < 1e-9
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(numerical_passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"float evaluation gives {numeric_val}, expected 900.0.",
        }
    )

    # A second symbolic consistency check using exact radicals.
    exact_sqrt = sqrt(Integer(1000000))
    exact_cuberoot = Integer(1000000) ** Rational(1, 3)
    consistency_passed = (exact_sqrt == Integer(1000)) and (exact_cuberoot == Integer(100))
    checks.append(
        {
            "name": "exact_root_values",
            "passed": bool(consistency_passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sqrt(1000000) -> {exact_sqrt!r}, 1000000**(1/3) -> {exact_cuberoot!r}.",
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)