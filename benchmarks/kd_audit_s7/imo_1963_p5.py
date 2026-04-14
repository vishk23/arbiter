from sympy import Symbol, cos, sin, pi, Rational, simplify, N, minimal_polynomial


def verify():
    checks = []
    proved = True

    # Verified symbolic proof using algebraic number theory.
    # Let E = cos(pi/7) - cos(2pi/7) + cos(3pi/7) - 1/2.
    # We prove E = 0 by showing its minimal polynomial is x.
    x = Symbol('x')
    expr = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7) - Rational(1, 2)
    try:
        mp = minimal_polynomial(expr, x)
        passed = (mp == x)
        checks.append({
            "name": "symbolic_trig_identity",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(expr, x) returned {mp!s}; expected x."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "symbolic_trig_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic proof failed with exception: {type(e).__name__}: {e}"
        })
        proved = False

    # Numerical sanity check at high precision.
    try:
        lhs = N(cos(pi/7) - cos(2*pi/7) + cos(3*pi/7), 50)
        rhs = N(Rational(1, 2), 50)
        diff = abs(lhs - rhs)
        passed = diff < 1e-45
        checks.append({
            "name": "numerical_sanity",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"lhs={lhs}, rhs={rhs}, abs diff={diff}."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed with exception: {type(e).__name__}: {e}"
        })
        proved = False

    # Additional symbolic consistency check from the hint.
    try:
        S = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7)
        transformed = simplify(S - (cos(pi/7) + cos(3*pi/7) + cos(5*pi/7)))
        passed = (transformed == 0)
        checks.append({
            "name": "trig_rewrite_consistency",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"simplify(S - (cos(pi/7)+cos(3pi/7)+cos(5pi/7))) returned {transformed!s}."
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "trig_rewrite_consistency",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Rewrite check failed with exception: {type(e).__name__}: {e}"
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)