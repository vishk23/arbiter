import math
from sympy import symbols, sqrt, Rational, Interval, simplify, minimal_polynomial, Symbol, N


def verify():
    checks = []

    x = symbols('x', real=True)
    alpha = 1 - sqrt(127) / 32

    # Check 1: exact symbolic proof that alpha satisfies the boundary equation
    # sqrt(sqrt(3-alpha) - sqrt(alpha+1)) = 1/2
    # We prove expr == 0 via minimal polynomial == t.
    try:
        t = Symbol('t')
        expr = sqrt(sqrt(3 - alpha) - sqrt(alpha + 1)) - Rational(1, 2)
        mp = minimal_polynomial(simplify(expr), t)
        passed = simplify(mp - t) == 0
        checks.append({
            "name": "boundary_point_exact",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(expr, t) = {mp}; expected t for expr = 0"
        })
    except Exception as e:
        checks.append({
            "name": "boundary_point_exact",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy exact proof failed: {e}"
        })

    # Check 2: exact symbolic proof that alpha is the smaller root of 1024 x^2 - 2048 x + 897 = 0
    try:
        t = Symbol('t')
        poly_expr = simplify(1024 * alpha**2 - 2048 * alpha + 897)
        mp2 = minimal_polynomial(poly_expr, t)
        passed = simplify(mp2 - t) == 0
        checks.append({
            "name": "alpha_quadratic_root_exact",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"minimal_polynomial(1024*alpha^2-2048*alpha+897, t) = {mp2}"
        })
    except Exception as e:
        checks.append({
            "name": "alpha_quadratic_root_exact",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Quadratic-root exact proof failed: {e}"
        })

    # Check 3: exact symbolic proof of endpoint inclusion x = -1
    try:
        t = Symbol('t')
        expr_left = sqrt(sqrt(3 - Rational(-1)) - sqrt(Rational(-1) + 1)) - Rational(1, 2)
        mp3 = minimal_polynomial(simplify(expr_left - (2 - Rational(1, 2))), t)
        passed = simplify(mp3 - t) == 0
        checks.append({
            "name": "left_endpoint_included_exact",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Verified f(-1)=2^(1/2)? equivalent exact zero certificate via minimal polynomial {mp3}"
        })
    except Exception as e:
        checks.append({
            "name": "left_endpoint_included_exact",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Left endpoint exact proof failed: {e}"
        })

    # Numerical sanity checks
    def lhs(val):
        return math.sqrt(math.sqrt(3 - val) - math.sqrt(val + 1))

    try:
        a_val = float(N(alpha, 50))
        pts = [
            (-1.0, True),
            (0.0, True),
            (a_val - 1e-6, True),
            (a_val + 1e-6, False),
            (1.0, False),
        ]
        ok = True
        details_parts = []
        for pt, expected in pts:
            value = lhs(pt)
            got = value > 0.5
            ok = ok and (got == expected)
            details_parts.append(f"x={pt:.12f}: lhs={value:.12f}, lhs>1/2 is {got}, expected {expected}")
        checks.append({
            "name": "numerical_sanity_samples",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(details_parts)
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_samples",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}"
        })

    # Check 5: symbolic interval equality using SymPy's solver as a consistency check.
    # This is not counted as a certificate proof type, but provides exact closed-form confirmation.
    try:
        from sympy import solve_univariate_inequality
        sol = solve_univariate_inequality(sqrt(sqrt(3 - x) - sqrt(x + 1)) > Rational(1, 2), x, relational=False)
        expected = Interval.Ropen(-1, alpha)
        passed = simplify(sol == expected)
        checks.append({
            "name": "solver_interval_match",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy returned solution set {sol}; expected {expected}. This is a consistency check, not a certificate."
        })
    except Exception as e:
        checks.append({
            "name": "solver_interval_match",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy interval solve failed: {e}"
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2, default=str))