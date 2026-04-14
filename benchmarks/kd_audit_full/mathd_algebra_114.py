from sympy import Symbol, Integer, Rational, sqrt, simplify, N


def verify():
    checks = []
    proved = True

    # Check 1: symbolic simplification of the expression for a = 8
    try:
        a = Integer(8)
        expr = (16 * (a**2) ** Rational(1, 3)) ** Rational(1, 3)
        simplified = simplify(expr)
        passed = simplified == Integer(4)
        checks.append(
            {
                "name": "symbolic_value_is_four",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Simplified expression to {simplified!s}; expected 4.",
            }
        )
        proved = proved and passed
    except Exception as e:
        checks.append(
            {
                "name": "symbolic_value_is_four",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy verification failed: {e}",
            }
        )
        proved = False

    # Check 2: verified algebraic certificate that 64^(1/3) = 4
    try:
        x = Symbol('x')
        expr = Integer(64) ** Rational(1, 3) - Integer(4)
        mp = expr.minimal_polynomial(x)
        passed = mp == x
        checks.append(
            {
                "name": "cube_root_of_sixty_four_is_four",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"minimal_polynomial(64^(1/3) - 4, x) = {mp}; expected x.",
            }
        )
        proved = proved and passed
    except Exception as e:
        checks.append(
            {
                "name": "cube_root_of_sixty_four_is_four",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Algebraic certificate failed: {e}",
            }
        )
        proved = False

    # Check 3: numerical sanity check
    try:
        a = 8
        val = float((16 * (a**2) ** (1/3)) ** (1/3))
        passed = abs(val - 4.0) < 1e-12
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical value evaluated to {val:.15f}; expected 4.0.",
            }
        )
        proved = proved and passed
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)