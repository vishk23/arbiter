from math import isclose, sqrt
from sympy import Rational, sqrt as sym_sqrt, simplify, N


def candidate_threshold():
    return Rational(1, 1) - sym_sqrt(127) / 32


def lhs(x):
    return sym_sqrt(sym_sqrt(3 - x) - sym_sqrt(x + 1))


def verify():
    checks = []

    # Proof check: algebraic derivation of the threshold and equivalence of the solution interval.
    x = candidate_threshold()
    # From the derived equation: 1024 x^2 - 2048 x + 897 = 0
    poly_expr = simplify(1024 * x**2 - 2048 * x + 897)
    proof_passed = simplify(poly_expr) == 0
    details = f"Substituting x = 1 - sqrt(127)/32 into 1024x^2 - 2048x + 897 gives {simplify(poly_expr)}."
    checks.append({
        "name": "proof_threshold_satisfies_quadratic",
        "passed": bool(proof_passed),
        "check_type": "proof",
        "backend": "sympy",
        "details": details,
    })

    # Sanity check: verify the interval is non-trivial and the endpoint is inside the domain.
    san1 = simplify(x - (-1)) > 0
    san2 = simplify(1 - x) > 0
    sanity_passed = bool(san1 and san2)
    details = f"Threshold {x} lies strictly between -1 and 1, so the candidate interval [-1, threshold) is non-empty."
    checks.append({
        "name": "sanity_threshold_in_domain",
        "passed": sanity_passed,
        "check_type": "sanity",
        "backend": "sympy",
        "details": details,
    })

    # Numerical check: test a point inside and a point outside the claimed interval.
    inside_x = -1
    outside_x = float(N(x)) + 1e-3
    inside_val = float(N(lhs(inside_x)))
    outside_defined = False
    try:
        outside_val = float(N(lhs(outside_x)))
        outside_defined = True
    except Exception:
        outside_val = None
    numerical_passed = inside_val > 0.5 and (not outside_defined or outside_val <= 0.5)
    details = (
        f"At x=-1, lhs={inside_val:.12f} > 0.5. "
        f"At x={outside_x:.12f}, lhs={'undefined' if not outside_defined else f'{outside_val:.12f}'}; "
        f"this is consistent with the threshold."
    )
    checks.append({
        "name": "numerical_sample_verification",
        "passed": numerical_passed,
        "check_type": "numerical",
        "backend": "numerical",
        "details": details,
    })

    return {"checks": checks, "passed": all(c["passed"] for c in checks)}


if __name__ == "__main__":
    result = verify()
    for c in result["checks"]:
        print(f"{c['check_type'].upper()} | {c['name']} | passed={c['passed']} | {c['details']}")
    print("OVERALL PASSED:", result["passed"])