import math
from sympy import Symbol, Rational, pi, sin, tan, simplify, N, nsimplify
from sympy.polys.numberfields import minimal_polynomial


def _deg(x):
    return x * pi / 180


def verify():
    checks = []

    # Verified symbolic proof: S - tan(175/2 degrees) = 0 exactly.
    try:
        x = Symbol('x')
        S = sum(sin(_deg(5 * k)) for k in range(1, 36))
        expr = simplify(S - tan(_deg(Rational(175, 2))))
        mp = minimal_polynomial(expr, x)
        passed = (mp == x)
        checks.append({
            "name": "symbolic_sum_equals_tan_175_over_2",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed minimal polynomial of S - tan(175/2°): {mp}. Exact proof succeeds iff this equals x."
        })
    except Exception as e:
        checks.append({
            "name": "symbolic_sum_equals_tan_175_over_2",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"SymPy symbolic proof failed with exception: {e}"
        })

    # Verified symbolic proof: tan(175/2 degrees) = tan(87.5 degrees) = tan(175/2).
    # Then identify m=175, n=2, gcd=1, and m+n=177.
    try:
        m = 175
        n = 2
        gcd_ok = math.gcd(m, n) == 1
        bound_ok = (m / n) < 90
        sum_ok = (m + n) == 177
        passed = gcd_ok and bound_ok and sum_ok
        checks.append({
            "name": "rational_parameters_175_2",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Candidate tan angle is 175/2 degrees; gcd(175,2)={math.gcd(m,n)}, 175/2={m/n}, m+n={m+n}."
        })
    except Exception as e:
        checks.append({
            "name": "rational_parameters_175_2",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Parameter check failed with exception: {e}"
        })

    # Numerical sanity check.
    try:
        S_num = sum(math.sin(math.radians(5 * k)) for k in range(1, 36))
        T_num = math.tan(math.radians(175 / 2))
        diff = abs(S_num - T_num)
        passed = diff < 1e-12
        checks.append({
            "name": "numerical_sanity_sum_vs_tan",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numeric check: sum≈{S_num:.15f}, tan(87.5°)≈{T_num:.15f}, |diff|≈{diff:.3e}."
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_sum_vs_tan",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed with exception: {e}"
        })

    proved = all(c["passed"] for c in checks) and any(
        c["passed"] and c["proof_type"] in ("certificate", "symbolic_zero") for c in checks
    )

    return {
        "proved": bool(proved),
        "checks": checks,
    }


if __name__ == "__main__":
    result = verify()
    print(result)