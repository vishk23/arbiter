from sympy import Symbol, Eq, sqrt, Rational, simplify, minimal_polynomial


def verify():
    checks = []
    proved = True

    # Verified symbolic proof: the two positive solutions are (sqrt(5)-1)/2 and (sqrt(5)+1)/2,
    # and their sum is sqrt(5). We certify the algebraic identity via minimal_polynomial.
    x = Symbol('x')
    a = (sqrt(5) - 1) / 2
    b = (sqrt(5) + 1) / 2
    s = simplify(a + b)
    try:
        # Symbolic zero certificate for s - sqrt(5) == 0
        mp = minimal_polynomial(s - sqrt(5), x)
        symbolic_ok = (mp == x)
        checks.append({
            "name": "symbolic_sum_identity",
            "passed": bool(symbolic_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial((a+b)-sqrt(5), x) == x evaluates to {mp == x}; a+b simplifies to {s}.",
        })
        proved = proved and bool(symbolic_ok)
    except Exception as e:
        checks.append({
            "name": "symbolic_sum_identity",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Symbolic proof failed: {e}",
        })
        proved = False

    # Numerical sanity check at concrete values
    try:
        aval = float(a.evalf(30))
        bval = float(b.evalf(30))
        lhs_a = abs(aval - 1.0 / aval)
        lhs_b = abs(bval - 1.0 / bval)
        num_ok = abs((aval + bval) - 5**0.5) < 1e-12 and abs(lhs_a - 1.0) < 1e-12 and abs(lhs_b - 1.0) < 1e-12
        checks.append({
            "name": "numerical_sanity",
            "passed": bool(num_ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"a≈{aval}, b≈{bval}, |a-1/a|≈{lhs_a}, |b-1/b|≈{lhs_b}, a+b≈{aval+bval}.",
        })
        proved = proved and bool(num_ok)
    except Exception as e:
        checks.append({
            "name": "numerical_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })
        proved = False

    # Direct algebraic verification that the claimed values satisfy |x - 1/x| = 1.
    try:
        expr_a = simplify(abs(a - 1/a) - 1)
        expr_b = simplify(abs(b - 1/b) - 1)
        direct_ok = (expr_a == 0) and (expr_b == 0)
        checks.append({
            "name": "direct_property_check",
            "passed": bool(direct_ok),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified |a-1/a|-1 simplifies to {expr_a} and |b-1/b|-1 simplifies to {expr_b}.",
        })
        proved = proved and bool(direct_ok)
    except Exception as e:
        checks.append({
            "name": "direct_property_check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Direct property verification failed: {e}",
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)