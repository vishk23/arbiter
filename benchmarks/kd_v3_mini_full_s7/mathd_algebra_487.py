import kdrag as kd
from kdrag.smt import *
from sympy import Symbol, Eq, solve, simplify, sqrt, Rational, minimal_polynomial, N


def verify():
    checks = []
    proved = True

    # Certified algebraic check: solve the intersection equation exactly.
    x = Symbol('x', real=True)
    roots = solve(Eq(x**2 + x - 1, 0), x)

    if len(roots) != 2:
        checks.append({
            'name': 'quadratic_roots_count',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Expected 2 exact roots, got {len(roots)}.'
        })
        proved = False
    else:
        r1, r2 = roots
        # Exact points on the parabola y=x^2.
        p1 = (r1, simplify(r1**2))
        p2 = (r2, simplify(r2**2))

        # Certified symbolic computation of squared distance.
        d2 = simplify((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)
        passed_symbolic = simplify(d2 - 10) == 0

        checks.append({
            'name': 'distance_squared_symbolic',
            'passed': passed_symbolic,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Exact intersection points are {p1} and {p2}; squared distance simplifies to {d2}. Hence distance = sqrt(10).'
        })
        if not passed_symbolic:
            proved = False

    # Additional certified proof using a direct algebraic derivation in kdrag.
    # Let the two x-coordinates be r1 and r2, the roots of x^2 + x - 1 = 0.
    # By Vieta, r1 + r2 = -1 and r1*r2 = -1, so (r1-r2)^2 = (r1+r2)^2 - 4r1r2 = 1 + 4 = 5.
    # The corresponding y-values are r1^2 and r2^2, so
    #   (r1^2-r2^2)^2 = (r1-r2)^2 (r1+r2)^2 = 5*1 = 5,
    # and the geometric distance between points on the parabola and line simplifies to sqrt(10).
    # We certify the key algebraic fact via kdrag: if x is a root of x^2+x-1=0, then x^2 = 1-x.
    xr = Real('xr')
    root_axiom = kd.prove(ForAll([xr], Implies(xr * xr + xr - 1 == 0, xr * xr == 1 - xr)))
    checks.append({
        'name': 'root_quadratic_relation_certificate',
        'passed': True,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': f'kd.prove certified the implication from x^2 + x - 1 = 0 to x^2 = 1 - x. Proof: {root_axiom}'
    })

    # Numerical sanity check at the exact roots returned by SymPy.
    if len(roots) == 2:
        d2_num = N(d2, 30)
        sqrt10_num = N(sqrt(10), 30)
        num_passed = abs(float(d2_num - 10)) < 1e-20 and abs(float(sqrt(d2_num)) - float(sqrt10_num)) < 1e-12
        checks.append({
            'name': 'numerical_sanity_distance',
            'passed': num_passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerically, squared distance ≈ {d2_num}, and sqrt(squared distance) ≈ {sqrt(d2_num)} ≈ {sqrt10_num}.'
        })
        if not num_passed:
            proved = False

    # Final conclusion check, based on the certified symbolic computation.
    if len(roots) == 2:
        final_passed = simplify(d2 - 10) == 0
        checks.append({
            'name': 'final_conclusion',
            'passed': final_passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'The squared distance is exactly 10, therefore the distance is exactly sqrt(10).'
        })
        if not final_passed:
            proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())