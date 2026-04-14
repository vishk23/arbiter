from sympy import Symbol, sqrt, Rational, minimal_polynomial, simplify

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:
    kd = None


def verify():
    checks = []
    proved_all = True

    # Intended exact solution: a = (1 + sqrt(5)) / 2.
    # This satisfies a^2 - a - 1 = 0.
    phi = (1 + sqrt(5)) / 2
    poly_expr = simplify(phi**2 - phi - 1)
    if poly_expr == 0:
        checks.append({
            "name": "golden_ratio_polynomial",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "Verified symbolically that phi = (1+sqrt(5))/2 is a root of a^2 - a - 1 = 0."
        })
    else:
        proved_all = False
        checks.append({
            "name": "golden_ratio_polynomial",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Unexpected nonzero simplification: {poly_expr}"
        })

    # Exact evaluation of the target expression at phi.
    target = simplify(phi**12 - 144 * (1 / phi))
    if target == 233:
        checks.append({
            "name": "target_value_exact",
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "Exact symbolic evaluation gives 233."
        })
    else:
        proved_all = False
        checks.append({
            "name": "target_value_exact",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Exact evaluation produced {target}, not 233."
        })

    # Minimal polynomial check for the golden ratio.
    x = Symbol('x')
    mp = minimal_polynomial(phi, x)
    if simplify(mp - (x**2 - x - 1)) == 0:
        checks.append({
            "name": "minimal_polynomial_phi",
            "passed": True,
            "backend": "sympy",
            "proof_type": "minimal_polynomial",
            "details": "SymPy minimal polynomial matches x^2 - x - 1."
        })
    else:
        proved_all = False
        checks.append({
            "name": "minimal_polynomial_phi",
            "passed": False,
            "backend": "sympy",
            "proof_type": "minimal_polynomial",
            "details": f"Unexpected minimal polynomial: {mp}"
        })

    return checks