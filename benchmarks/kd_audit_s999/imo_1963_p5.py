from sympy import Symbol, Rational, cos, sin, pi, simplify, minimal_polynomial, N


def _symbolic_proof():
    x = Symbol('x')
    expr = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7) - Rational(1, 2)
    mp = minimal_polynomial(expr, x)
    return mp == x, mp


def _numerical_check():
    expr = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7) - Rational(1, 2)
    val = N(expr, 50)
    return abs(complex(val)) < 1e-45, val


def _algebraic_identity_check():
    # Direct symbolic simplification of the transformed expression from the hint.
    s = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7)
    transformed = cos(pi/7) + cos(3*pi/7) + cos(5*pi/7)
    # These are exactly equal since cos(5*pi/7) = -cos(2*pi/7).
    return simplify(s - transformed) == 0, simplify(s - transformed)


def verify():
    checks = []

    passed, mp = _symbolic_proof()
    checks.append({
        "name": "symbolic_zero_minimal_polynomial",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"minimal_polynomial(expr - 1/2, x) = {mp}",
    })

    passed2, diff = _algebraic_identity_check()
    checks.append({
        "name": "trig_rewrite_identity",
        "passed": bool(passed2),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Difference after rewrite simplifies to: {diff}",
    })

    passed3, val = _numerical_check()
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(passed3),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"expr - 1/2 evaluated to {val}",
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)