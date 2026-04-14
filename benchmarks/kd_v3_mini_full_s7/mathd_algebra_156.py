import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: Verified proof by factoring the intersection equation.
    # Let u = x^2. Then u^2 - 5u + 6 = 0, whose roots are 2 and 3.
    x = Real('x')
    u = Real('u')
    thm1 = None
    try:
        thm1 = kd.prove(
            ForAll([u], Implies(u * u - 5 * u + 6 == 0, Or(u == 2, u == 3)))
        )
        checks.append({
            'name': 'factorization_roots_of_quadratic',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kd.prove() certified that any real u satisfying u^2 - 5u + 6 = 0 must be 2 or 3.'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'factorization_roots_of_quadratic',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}'
        })

    # Check 2: Verified proof that the desired difference is 1, using the roots 3 and 2.
    try:
        thm2 = kd.prove(3 - 2 == 1)
        checks.append({
            'name': 'difference_m_minus_n',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'kd.prove() certified that 3 - 2 = 1, hence m - n = 1 once m = 3 and n = 2.'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'difference_m_minus_n',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}'
        })

    # Check 3: SymPy symbolic verification of the algebraic factorization.
    try:
        x_sym = sp.symbols('x', real=True)
        expr = sp.expand(x_sym**4 - 5*x_sym**2 + 6)
        factored = sp.factor(expr)
        passed = sp.simplify(factored - (x_sym**2 - 3)*(x_sym**2 - 2)) == 0
        if passed:
            checks.append({
                'name': 'symbolic_factorization',
                'passed': True,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'SymPy verified x^4 - 5x^2 + 6 factors as {factored} = (x^2 - 3)(x^2 - 2).'
            })
        else:
            proved = False
            checks.append({
                'name': 'symbolic_factorization',
                'passed': False,
                'backend': 'sympy',
                'proof_type': 'symbolic_zero',
                'details': f'Unexpected factorization result: {factored}'
            })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'symbolic_factorization',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy check failed: {e}'
        })

    # Check 4: Numerical sanity check at a concrete intersection point x = sqrt(2).
    try:
        val_left = float((sp.sqrt(2))**4)
        val_right = float(5*(sp.sqrt(2))**2 - 6)
        passed = abs(val_left - val_right) < 1e-12
        checks.append({
            'name': 'numerical_sanity_at_sqrt2',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'At x=sqrt(2), y_left={val_left}, y_right={val_right}; difference={abs(val_left - val_right)}.'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_at_sqrt2',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)