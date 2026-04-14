import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []

    # Check 1: Verified proof in kdrag that the positive integer solution is 16,
    # hence the greater consecutive even integer is 18.
    try:
        x = Int('x')
        thm = kd.prove(
            ForAll([x],
                Implies(And(x > 0, x * (x + 2) == 288), Or(x == 16, x == -18))
            )
        )
        checks.append({
            'name': 'z3_certificate_solution_classification',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned proof: {thm}'
        })
    except Exception as e:
        checks.append({
            'name': 'z3_certificate_solution_classification',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Check 2: SymPy symbolic verification that the equation factors as claimed.
    try:
        x = sp.symbols('x', integer=True)
        expr = sp.expand(x * (x + 2) - 288)
        factored = sp.factor(expr)
        passed = sp.simplify(factored - (x - 16) * (x + 18)) == 0
        checks.append({
            'name': 'sympy_factorization',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'expanded={expr}, factored={factored}'
        })
    except Exception as e:
        checks.append({
            'name': 'sympy_factorization',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy check failed: {type(e).__name__}: {e}'
        })

    # Check 3: Numerical sanity check for the claimed integers 16 and 18.
    try:
        a, b = 16, 18
        passed = (a > 0 and b > 0 and b == a + 2 and a * b == 288)
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Checked ({a}, {b}): consecutive even positive integers and product {a*b}'
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)