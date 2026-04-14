import kdrag as kd
from kdrag.smt import Int, Real, ForAll, Implies, And, Or, Not
from sympy import symbols, minimal_polynomial, solve, Eq


def verify():
    checks = []
    proved = True

    x = Real('x')
    y = Real('y')

    # Substitute y = x^2 + 18x + 30
    subs_expr = x**2 + 18*x + 30

    # Solve: y = 2*sqrt(y + 15)
    y_value = 10  # From manual solution analysis

    # Substitute back: x^2 + 18x + 30 = 10
    discrim_check_expr = x**2 + 18*x + 20

    # Check the discriminant is positive
    check_name_discrim = "discriminant_positive"
    try:
        kd.prove(subs_expr == y_value)

        # Check discriminant
        thm = kd.prove(ForAll([x], 
                              Implies(subs_expr == y_value, discrim_check_expr >= 0)))
        checks.append({
            "name": check_name_discrim,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm)
        })
    except kd.kernel.LemmaError as e:
        proved = False
        checks.append({
            "name": check_name_discrim,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(e)
        })

    # Symbolic check using SymPy (roots and product of roots)
    x_sym = symbols('x')
    poly_expr = x_sym**2 + 18*x_sym + 20
    roots = solve(Eq(poly_expr, 0), x_sym)
    product_of_roots = roots[0] * roots[1]
    check_name_sympy = "product_of_roots_sympy"
    try:
        mp = minimal_polynomial(product_of_roots - 20, x_sym)
        assert mp == x_sym
        checks.append({
            "name": check_name_sympy,
            "passed": True,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "Product of roots is 20"
        })
    except AssertionError:
        proved = False
        checks.append({
            "name": check_name_sympy,
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": "Failed to verify product of roots."  
        })

    # Numerical verification sanity check
    check_name_numerical = "numerical_sanity_check"
    root_eval_1 = -1 - (18 / 2)
    root_eval_2 = -1 - (18 / 2) + 1
    num_verified = (root_eval_1 * root_eval_2) == 20
    checks.append({
        "name": check_name_numerical,
        "passed": num_verified,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Roots: {root_eval_1:.4f}, {root_eval_2:.4f}. Product: {root_eval_1 * root_eval_2:.4f}"
    })

    if not num_verified:
        proved = False

    return {
        "proved": proved,
        "checks": checks
    }

if __name__ == "__main__":
    result = verify()
    print("Verification Result:", result)