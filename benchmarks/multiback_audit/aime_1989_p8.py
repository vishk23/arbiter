from sympy import symbols, Eq, solve, simplify


def verify():
    checks = []

    # Symbols for the linear coefficients in f(k) = a k^2 + b k + c
    a, b, c = symbols('a b c', real=True)

    # Solve the system coming from f(1), f(2), f(3)
    eq1 = Eq(a + b + c, 1)
    eq2 = Eq(4*a + 2*b + c, 12)
    eq3 = Eq(9*a + 3*b + c, 123)
    sol = solve((eq1, eq2, eq3), (a, b, c), dict=True)

    # PROOF: derive f(4) = 334 from the solved coefficients
    proof_passed = False
    proof_details = ''
    if sol:
        s = sol[0]
        f4 = simplify(16*s[a] + 4*s[b] + s[c])
        proof_passed = (f4 == 334)
        proof_details = f'solution={s}, f(4)={f4}'
    else:
        proof_details = 'No solution returned by symbolic solver.'

    checks.append({
        'name': 'proof_f4_equals_334',
        'passed': proof_passed,
        'check_type': 'proof',
        'backend': 'sympy',
        'details': proof_details,
    })

    # SANITY: confirm the system is non-trivial and has a unique symbolic solution
    sanity_passed = bool(sol) and len(sol) == 1
    sanity_details = f'Number of symbolic solutions: {len(sol) if sol else 0}'
    checks.append({
        'name': 'sanity_unique_solution_exists',
        'passed': sanity_passed,
        'check_type': 'sanity',
        'backend': 'sympy',
        'details': sanity_details,
    })

    # NUMERICAL: verify with the explicit coefficients a=50, b=-139, c=90
    a_num, b_num, c_num = 50, -139, 90
    f1 = a_num + b_num + c_num
    f2 = 4*a_num + 2*b_num + c_num
    f3 = 9*a_num + 3*b_num + c_num
    f4 = 16*a_num + 4*b_num + c_num
    numerical_passed = (f1 == 1 and f2 == 12 and f3 == 123 and f4 == 334)
    numerical_details = f'f(1)={f1}, f(2)={f2}, f(3)={f3}, f(4)={f4}'
    checks.append({
        'name': 'numerical_verify_values',
        'passed': numerical_passed,
        'check_type': 'numerical',
        'backend': 'numerical',
        'details': numerical_details,
    })

    return {'proved': all(c['passed'] for c in checks), 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)