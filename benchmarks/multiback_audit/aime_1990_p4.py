from sympy import symbols, Eq, factor, simplify, solve


def verify():
    results = []

    # Symbolic proof using the hinted substitution a = x^2 - 10x - 29.
    x, a = symbols('x a', real=True)

    # The transformed equation:
    # 1/a + 1/(a-16) - 2/(a-40) = 0
    lhs = 1/a + 1/(a - 16) - 2/(a - 40)
    num = simplify((a * (a - 16) * (a - 40)) * lhs)
    # This should simplify to -64*(a - 10)
    proof_passed = simplify(num + 64 * (a - 10)) == 0
    results.append({
        'name': 'proof_reduction_to_linear_equation',
        'passed': bool(proof_passed),
        'check_type': 'proof',
        'backend': 'sympy',
        'details': f'Cleared numerator simplifies to {num}; expected -64*(a - 10).'
    })

    # Sanity check: confirm the original transformation is non-trivial and the factorization works.
    poly = x**2 - 10*x - 29 - 10
    factored = factor(poly)
    sanity_passed = simplify(factored - (x - 13)*(x + 3)) == 0
    results.append({
        'name': 'sanity_factorization_nontrivial',
        'passed': bool(sanity_passed),
        'check_type': 'sanity',
        'backend': 'sympy',
        'details': f'(x^2 - 10x - 29) - 10 factors as {factored}, matching (x - 13)(x + 3).'
    })

    # Numerical check at the positive solution x = 13.
    x_val = 13
    denom1 = x_val**2 - 10*x_val - 29
    denom2 = x_val**2 - 10*x_val - 45
    denom3 = x_val**2 - 10*x_val - 69
    numeric_expr = 1/denom1 + 1/denom2 - 2/denom3
    numerical_passed = simplify(numeric_expr) == 0
    results.append({
        'name': 'numerical_evaluation_at_13',
        'passed': bool(numerical_passed),
        'check_type': 'numerical',
        'backend': 'numerical',
        'details': f'At x=13, denominators are {denom1}, {denom2}, {denom3}; expression evaluates to {numeric_expr}.'
    })

    return {"proved": all(r['passed'] for r in results), "checks": results}


if __name__ == "__main__":
    out = verify()
    for chk in out["checks"]:
        print(f"{chk['name']}: {chk['passed']} ({chk['check_type']}, {chk['backend']}) - {chk['details']}")
    print("PROVED" if out["proved"] else "NOT PROVED")