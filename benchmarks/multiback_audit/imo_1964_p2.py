from sympy import symbols, expand, simplify, factor


def verify():
    checks = []

    # Symbols
    x, y, z = symbols('x y z', nonnegative=True, real=True)
    a, b, c = symbols('a b c', positive=True, real=True)

    # Algebraic transformation:
    # a = x+y, b = x+z, c = y+z
    lhs = a**2 * (b + c - a) + b**2 * (c + a - b) + c**2 * (a + b - c)
    rhs = 3 * a * b * c

    subs_map = {a: x + y, b: x + z, c: y + z}
    lhs_sub = expand(lhs.subs(subs_map))
    rhs_sub = expand(rhs.subs(subs_map))
    diff_sub = simplify(rhs_sub - lhs_sub)

    # PROOF check: after substitution, the inequality becomes
    # 3abc - LHS = x^2y + x^2z + y^2x + y^2z + z^2x + z^2y - 6xyz
    # which is nonnegative by AM-GM.
    target = x**2*y + x**2*z + y**2*x + y**2*z + z**2*x + z**2*y - 6*x*y*z
    proof_passed = simplify(diff_sub - target) == 0
    checks.append({
        'name': 'proof_algebraic_reduction',
        'passed': bool(proof_passed),
        'check_type': 'proof',
        'backend': 'sympy',
        'details': f'reduced difference simplifies to target expression: {proof_passed}'
    })

    # SANITY check: the reduction is non-trivial and the target is not identically zero.
    sanity_passed = simplify(target) != 0 and factor(target) != 0
    checks.append({
        'name': 'sanity_nontrivial_expression',
        'passed': bool(sanity_passed),
        'check_type': 'sanity',
        'backend': 'sympy',
        'details': 'target expression is nonzero symbolic polynomial' if sanity_passed else 'unexpected zero polynomial'
    })

    # NUMERICAL check: choose a triangle, e.g. a=3, b=4, c=5.
    aval, bval, cval = 3, 4, 5
    lhs_num = (aval**2) * (bval + cval - aval) + (bval**2) * (cval + aval - bval) + (cval**2) * (aval + bval - cval)
    rhs_num = 3 * aval * bval * cval
    numerical_passed = lhs_num <= rhs_num
    checks.append({
        'name': 'numerical_example_3_4_5',
        'passed': bool(numerical_passed),
        'check_type': 'numerical',
        'backend': 'numerical',
        'details': f'LHS={lhs_num}, RHS={rhs_num}'
    })

    return {'checks': checks, 'proved': all(c['passed'] for c in checks)}


if __name__ == '__main__':
    result = verify()
    for chk in result['checks']:
        print(chk)
    print('PROVED' if result['proved'] else 'NOT PROVED')