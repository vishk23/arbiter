from sympy import Symbol, cos, pi, minimal_polynomial, N, Rational


def verify():
    checks = []
    x = Symbol('x')
    # Define the expression
    expr = cos(pi/7) - cos(2*pi/7) + cos(3*pi/7) 
    
    # Symbolic proof
    try:
        mp = minimal_polynomial(expr - Rational(1, 2), x)
        proved = (mp == x)
        checks.append({
            "name": "Minimal Polynomial Check",
            "passed": proved,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": str(mp)
        })
    except Exception as e:
        checks.append({
            "name": "Minimal Polynomial Check",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": str(e)
        })
    
    # Numerical check
    numerical_value = N(expr)
    numerical_pass = abs(numerical_value - 0.5) < 1e-9
    checks.append({
        "name": "Numerical Value Check",
        "passed": numerical_pass,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Numerical value: {numerical_value}"
    })

    proved = all(check['passed'] for check in checks)
    return {
        "proved": proved,
        "checks": checks
    }


if __name__ == "__main__":
    result = verify()
    print(result)