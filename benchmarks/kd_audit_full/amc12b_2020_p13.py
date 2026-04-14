from sympy import Symbol, log, sqrt, N, simplify


def verify():
    checks = []
    proved = True

    # Check 1: symbolic identity for the target expression
    try:
        expr_left = sqrt(log(6, 2) + log(6, 3))
        expr_right = sqrt(log(3, 2)) + sqrt(log(2, 3))
        diff = simplify(expr_left - expr_right)
        passed = diff == 0
        checks.append({
            "name": "symbolic_identity_for_choice_D",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"simplify(left - right) -> {diff}"
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "symbolic_identity_for_choice_D",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e}"
        })
        proved = False

    # Check 2: numerical sanity check at concrete values
    try:
        expr_left_num = N(sqrt(log(6, 2) + log(6, 3)), 50)
        expr_right_num = N(sqrt(log(3, 2)) + sqrt(log(2, 3)), 50)
        passed = abs(expr_left_num - expr_right_num) < 10**(-45)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"left={expr_left_num}, right={expr_right_num}, abs diff={abs(expr_left_num - expr_right_num)}"
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })
        proved = False

    # Check 3: algebraic rewrite of the logarithms used in the proof hint
    try:
        a = log(3, 2)
        b = log(2, 3)
        expr = simplify(a * b)
        passed = expr == 1
        checks.append({
            "name": "log_inverse_property",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"simplify(log(3,2)*log(2,3)) -> {expr}"
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "log_inverse_property",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy verification failed: {e}"
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)