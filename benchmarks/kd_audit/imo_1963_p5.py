from sympy import Symbol, Rational, pi, cos, sin, simplify, trigsimp, N, minimal_polynomial


def verify():
    checks = []
    proved = True

    # Check 1: symbolic verification via algebraic zero / exact simplification
    name = "symbolic_trig_identity"
    try:
        expr = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7) - Rational(1, 2)
        # A rigorous symbolic certificate: exact simplification to zero.
        simplified = simplify(trigsimp(expr))
        passed = simplified == 0
        details = f"simplify(trigsimp(expr)) -> {simplified!r}"
        proof_type = "symbolic_zero"
    except Exception as e:
        passed = False
        proof_type = "symbolic_zero"
        details = f"Symbolic verification failed with exception: {e!r}"
    checks.append({
        "name": name,
        "passed": passed,
        "backend": "sympy",
        "proof_type": proof_type,
        "details": details,
    })
    proved = proved and passed

    # Check 2: rigorous algebraic certificate using minimal polynomial of the residual.
    # For a true zero, the minimal polynomial should be x.
    name = "minimal_polynomial_certificate"
    try:
        x = Symbol('x')
        residual = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7) - Rational(1, 2)
        mp = minimal_polynomial(residual, x)
        passed = (mp == x)
        details = f"minimal_polynomial(residual, x) -> {mp!r}"
        proof_type = "symbolic_zero"
    except Exception as e:
        passed = False
        proof_type = "symbolic_zero"
        details = f"Minimal polynomial computation failed with exception: {e!r}"
    checks.append({
        "name": name,
        "passed": passed,
        "backend": "sympy",
        "proof_type": proof_type,
        "details": details,
    })
    proved = proved and passed

    # Check 3: numerical sanity check at high precision.
    name = "numerical_sanity_check"
    try:
        val = N(cos(pi/7) - cos(2*pi/7) + cos(3*pi/7), 50)
        passed = abs(val - Rational(1, 2)) < 1e-45
        details = f"N(expr, 50) = {val}; difference from 1/2 = {N(val - Rational(1,2), 50)}"
        proof_type = "numerical"
    except Exception as e:
        passed = False
        proof_type = "numerical"
        details = f"Numerical evaluation failed with exception: {e!r}"
    checks.append({
        "name": name,
        "passed": passed,
        "backend": "numerical",
        "proof_type": proof_type,
        "details": details,
    })
    proved = proved and passed

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)