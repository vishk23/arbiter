from sympy import symbols, sqrt, I, exp, pi, simplify, Eq


def verify():
    checks = []

    # Check 1: symbolic computation of the rotated point
    try:
        z = 2 + sqrt(2) - (3 + 3*sqrt(2))*I
        c = 2 - 3*I
        w = simplify(c + (z - c) * exp(I * pi / 4))
        expected = 5 + 2*sqrt(2) + (-1 - sqrt(2))*I
        passed = simplify(w - expected) == 0
        checks.append({
            "name": "symbolic_rotation_result",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed w = {w}; expected {expected}."
        })
    except Exception as e:
        checks.append({
            "name": "symbolic_rotation_result",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic computation failed: {e}"
        })

    # Check 2: numerical sanity check at concrete values
    try:
        z_num = complex(2 + 2**0.5, -(3 + 3*2**0.5))
        c_num = complex(2, -3)
        rot = complex(2**0.5 / 2, 2**0.5 / 2)
        w_num = c_num + (z_num - c_num) * rot
        expected_num = complex(5 + 2*2**0.5, -(1 + 2**0.5))
        passed = abs(w_num - expected_num) < 1e-9
        checks.append({
            "name": "numerical_sanity_check",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"w_num={w_num}, expected_num={expected_num}."
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())