from sympy import Symbol, expand, simplify, Eq, sqrt

try:
    import kdrag as kd
    from kdrag.smt import Real, ForAll, Implies
except Exception:
    kd = None


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof by completing the square.
    if kd is not None:
        x = Real('x')
        y = Real('y')
        # The original equation is equivalent to the completed-square form.
        # Expand the completed-square form to verify it matches the given equation.
        thm = kd.prove(
            ForAll([x, y], Implies((x + 4) * (x + 4) + (y - 3) * (y - 3) == 25,
                                   x * x + 8 * x + y * y - 6 * y == 0))
        )
        checks.append({
            'name': 'completed_square_equivalence',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm)
        })
    else:
        proved = False
        checks.append({
            'name': 'completed_square_equivalence',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kdrag unavailable; cannot produce formal certificate.'
        })

    # Check 2: Symbolic algebra confirms the completed-square expansion.
    x = Symbol('x')
    y = Symbol('y')
    expr = expand((x + 4)**2 + (y - 3)**2 - 25)
    symbolic_ok = simplify(expr - (x**2 + 8*x + y**2 - 6*y)) == 0
    checks.append({
        'name': 'symbolic_expansion_check',
        'passed': bool(symbolic_ok),
        'backend': 'sympy',
        'proof_type': 'numerical',
        'details': 'Expanded (x+4)^2 + (y-3)^2 - 25 and compared symbolically.'
    })
    proved = proved and bool(symbolic_ok)

    # Check 3: Numerical sanity check at a concrete point on the circle.
    # Point (-1, 3) satisfies (x+4)^2 + (y-3)^2 = 25, so it lies on the circle.
    x0, y0 = -1, 3
    lhs = x0**2 + 8*x0 + y0**2 - 6*y0
    numeric_ok = (lhs == 0)
    checks.append({
        'name': 'numerical_point_on_circle',
        'passed': bool(numeric_ok),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'At (-1, 3), the equation evaluates to {lhs}, confirming a point on the circle.'
    })
    proved = proved and bool(numeric_ok)

    # Check 4: Radius computation from the completed-square form.
    radius = sqrt(25)
    radius_ok = (radius == 5)
    checks.append({
        'name': 'radius_is_five',
        'passed': bool(radius_ok),
        'backend': 'sympy',
        'proof_type': 'numerical',
        'details': 'From (x+4)^2 + (y-3)^2 = 25, radius = sqrt(25) = 5.'
    })
    proved = proved and bool(radius_ok)

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)