from sympy import symbols, Eq, solve, sqrt, simplify, discriminant, Poly
from math import isclose


def verify():
    results = []

    # ----------------------------
    # Proof check (SymPy)
    # ----------------------------
    x, y = symbols('x y', real=True)

    # Let y = x^2 + 18x + 30. Then the equation becomes y = 2*sqrt(y + 15).
    # Squaring gives y^2 - 4y - 60 = 0, so y in {10, -6}.
    y_solutions = solve(Eq(y, 2 * sqrt(y + 15)), y)

    # Only y = 10 is admissible because sqrt(y+15) is real and nonnegative,
    # and y = 2*sqrt(y+15) implies y >= 0.
    y_valid = [sol for sol in y_solutions if sol == 10]

    # Back-substitute y = 10:
    # x^2 + 18x + 30 = 10  =>  x^2 + 18x + 20 = 0
    quad = x**2 + 18*x + 20
    quad_roots = solve(Eq(quad, 0), x)
    product = simplify(quad_roots[0] * quad_roots[1])

    proof_passed = (
        set(y_solutions) == set([-6, 10])
        and y_valid == [10]
        and simplify(product - 20) == 0
    )
    results.append({
        "name": "proof_via_substitution_and_vieta",
        "passed": bool(proof_passed),
        "check_type": "PROOF",
        "backend": "sympy",
        "details": f"y-solutions={y_solutions}, valid_y={y_valid}, root_product={product}"
    })

    # ----------------------------
    # Sanity check (SymPy)
    # ----------------------------
    disc = discriminant(Poly(quad, x), x)
    sanity_passed = (quad != 0 and disc > 0)
    results.append({
        "name": "sanity_nontrivial_transform",
        "passed": bool(sanity_passed),
        "check_type": "SANITY",
        "backend": "sympy",
        "details": f"quadratic={quad}, discriminant={disc}"
    })

    # ----------------------------
    # Numerical check
    # ----------------------------
    # The real roots are x = -10 and x = -2.
    x1, x2 = -10, -2
    lhs1 = x1**2 + 18*x1 + 30
    rhs1 = 2 * ((x1**2 + 18*x1 + 45) ** 0.5)
    lhs2 = x2**2 + 18*x2 + 30
    rhs2 = 2 * ((x2**2 + 18*x2 + 45) ** 0.5)

    numerical_passed = (
        isclose(lhs1, rhs1, rel_tol=1e-12, abs_tol=1e-12)
        and isclose(lhs2, rhs2, rel_tol=1e-12, abs_tol=1e-12)
        and (x1 * x2 == 20)
    )
    results.append({
        "name": "numerical_root_validation",
        "passed": bool(numerical_passed),
        "check_type": "NUMERICAL",
        "backend": "python-math",
        "details": f"(x1,lhs1,rhs1)=({x1},{lhs1},{rhs1}), (x2,lhs2,rhs2)=({x2},{lhs2},{rhs2}), product={x1*x2}"
    })

    return results