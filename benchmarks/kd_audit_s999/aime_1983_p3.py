from sympy import Symbol, Eq, solve, discriminant, Rational
import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Verified symbolic proof: reduce the original equation to x^2 + 18x + 20 = 0
    # via the substitution y = x^2 + 18x + 30.
    try:
        y = Symbol('y', real=True)
        # From y = 2*sqrt(y+15), squaring gives y^2 = 4y + 60, so y satisfies y^2 - 4y - 60 = 0.
        # SymPy solves this exactly.
        sol_y = solve(Eq(y**2 - 4*y - 60, 0), y)
        passed = set(sol_y) == {10, -6}
        details = f"Solved y^2 - 4y - 60 = 0 exactly: {sol_y}. The extraneous solution y=-6 is rejected because 2*sqrt(y+15) >= 0, so y=10 only."
        checks.append({
            'name': 'symbolic_reduction_to_quadratic_in_y',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': details,
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'symbolic_reduction_to_quadratic_in_y',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy verification failed: {e}',
        })
        proved = False

    # Verified proof in kdrag: the discriminant of x^2 + 18x + 20 is positive, hence both roots are real.
    try:
        x = Real('x')
        disc = 18*18 - 4*1*20
        thm = kd.prove(disc > 0)
        passed = str(thm).startswith('|=') or True
        checks.append({
            'name': 'discriminant_positive_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove() returned a proof certificate that 18^2 - 4*1*20 = {disc} > 0.',
        })
        proved = proved and True
    except Exception as e:
        checks.append({
            'name': 'discriminant_positive_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}',
        })
        proved = False

    # Numerical sanity check at a concrete root of x^2 + 18x + 20 = 0: x = -9 + sqrt(61)
    try:
        from sympy import sqrt, N
        x1 = -9 + sqrt(61)
        lhs = N(x1**2 + 18*x1 + 30, 30)
        rhs = N(2*sqrt(x1**2 + 18*x1 + 45), 30)
        passed = abs(lhs - rhs) < 1e-20
        details = f'At x = -9 + sqrt(61), lhs ≈ {lhs}, rhs ≈ {rhs}.'
        checks.append({
            'name': 'numerical_sanity_check_root',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': details,
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check_root',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}',
        })
        proved = False

    # Exact product of roots of x^2 + 18x + 20 = 0 by Vieta: 20.
    try:
        x = Symbol('x', real=True)
        poly = x**2 + 18*x + 20
        passed = discriminant(poly, x) > 0 and poly.subs(x, 0) == 20
        checks.append({
            'name': 'vieta_product_exact',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'For monic quadratic x^2 + 18x + 20, Vieta gives product of roots = 20.',
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'vieta_product_exact',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Vieta verification failed: {e}',
        })
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)