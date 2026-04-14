from sympy import Symbol, Rational, simplify


def verify():
    checks = []

    # Check 1: symbolic algebraic derivation from the given condition.
    # Let x = r^(1/3). Then x + 1/x = 3.
    # Cubing gives x^3 + 1/x^3 + 3(x + 1/x) = 27, so x^3 + 1/x^3 = 18.
    # Since x^3 = r, this becomes r + 1/r = 18.
    # Cubing again: (r + 1/r)^3 = r^3 + 1/r^3 + 3(r + 1/r) = 18^3.
    # Therefore r^3 + 1/r^3 = 18^3 - 3*18 = 5778.
    try:
        expr = 18**3 - 3*18
        symbolic_ok = simplify(expr - 5778) == 0
        checks.append({
            "name": "symbolic_derivation",
            "passed": bool(symbolic_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed 18^3 - 3*18 = {expr}; matches 5778."
        })
    except Exception as e:
        checks.append({
            "name": "symbolic_derivation",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic verification failed: {e}"
        })

    # Check 2: numerical sanity check with a concrete real solution.
    # Solve x + 1/x = 3 => x = (3 + sqrt(5))/2 or (3 - sqrt(5))/2.
    # Take x = (3 + sqrt(5))/2 > 0, then r = x^3.
    # Verify numerically that r^3 + 1/r^3 = 5778.
    try:
        x = (3 + 5**0.5) / 2
        r = x**3
        lhs = r**3 + 1/(r**3)
        num_ok = abs(lhs - 5778) < 1e-9
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Using x=(3+sqrt(5))/2 gives r=x^3 and lhs={lhs}."
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}"
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)