from sympy import Symbol, Rational, pi, cos, sin, simplify, N, minimal_polynomial


def _exact_trig_identity():
    """Rigorous symbolic proof using exact algebraic computation in SymPy."""
    x = Symbol('x')
    expr = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7) - Rational(1, 2)
    mp = minimal_polynomial(expr, x)
    # For a rigorous zero certificate, the minimal polynomial of the exact algebraic
    # expression expr over Q must be x.
    return mp == x, mp, expr


def _numerical_sanity_check():
    expr = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7)
    val = N(expr, 50)
    target = N(Rational(1, 2), 50)
    diff = N(expr - Rational(1, 2), 50)
    passed = abs(diff) < 1e-40
    return passed, val, target, diff


def verify():
    checks = []
    proved = True

    # Verified symbolic certificate via minimal_polynomial.
    try:
        sym_ok, mp, expr = _exact_trig_identity()
        checks.append({
            "name": "exact_trig_identity",
            "passed": bool(sym_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(cos(pi/7) - cos(2*pi/7) + cos(3*pi/7) - 1/2, x) = {mp}",
        })
        proved = proved and sym_ok
    except Exception as e:
        checks.append({
            "name": "exact_trig_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic proof attempt failed: {type(e).__name__}: {e}",
        })
        proved = False

    # Numerical sanity check.
    try:
        num_ok, val, target, diff = _numerical_sanity_check()
        checks.append({
            "name": "numerical_sanity",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"expr≈{val}, target≈{target}, diff≈{diff}",
        })
        proved = proved and num_ok
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })
        proved = False

    return {"proved": bool(proved), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)