import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, sqrt, solve, simplify, Integer


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof with kdrag that the transformed equation implies y = 25.
    # We encode the key algebraic step from the hint:
    # y - 15 = 2*sqrt(y), with y >= 0, implies y = 25.
    y = Real('y')
    try:
        thm1 = kd.prove(
            ForAll([y], Implies(And(y >= 0, y - 15 == 2 * y ** (RealVal('1') / RealVal('2'))), y == 25))
        )
        checks.append({
            'name': 'transformed_equation_implies_y_equals_25',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kd.prove returned a proof that the nonnegative transformed equation forces y = 25.'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'transformed_equation_implies_y_equals_25',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Could not prove the transformed equation step with kdrag: {e}'
        })

    # Check 2: Verified symbolic algebra with SymPy on the reduced quadratic.
    x = symbols('x', real=True)
    try:
        # From x^2 + 18x + 20 = 0, product of roots is 20 by Vieta.
        # We verify the factorization explicitly.
        poly = x**2 + 18*x + 20
        roots = solve(Eq(poly, 0), x)
        # roots should be real and their product 20
        prod = simplify(roots[0] * roots[1])
        passed = simplify(prod - Integer(20)) == 0
        checks.append({
            'name': 'reduced_quadratic_root_product',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Solved x^2 + 18x + 20 = 0; root product simplifies to {prod}.'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'reduced_quadratic_root_product',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy verification failed: {e}'
        })

    # Check 3: Numerical sanity check at a concrete root.
    # x = -9 + sqrt(61) is one root of x^2 + 18x + 20 = 0.
    try:
        xr = -9 + sqrt(61)
        lhs = simplify(xr**2 + 18*xr + 30)
        rhs = simplify(2 * sqrt(xr**2 + 18*xr + 45))
        passed = simplify(lhs - rhs) == 0
        checks.append({
            'name': 'numerical_sanity_check_root',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Checked one concrete root x = -9 + sqrt(61): lhs={lhs}, rhs={rhs}.'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check_root',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical sanity check failed: {e}'
        })

    # Final summary: if the key proof step failed, the whole proof is not complete.
    if not all(ch['passed'] for ch in checks):
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)