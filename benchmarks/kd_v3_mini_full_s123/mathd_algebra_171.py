import kdrag as kd
from kdrag.smt import *
from sympy import symbols, simplify


def verify():
    checks = []

    # Verified proof: f(1) = 9 for f(x) = 5x + 4.
    # Encode the arithmetic claim directly in Z3 and obtain a proof certificate.
    x = Int('x')
    thm = None
    try:
        thm = kd.prove(5 * 1 + 4 == 9)
        checks.append({
            'name': 'evaluate_f_at_1_verified',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned proof object: {thm}',
        })
    except Exception as e:
        checks.append({
            'name': 'evaluate_f_at_1_verified',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}',
        })

    # Numerical sanity check at the concrete value x = 1.
    val = 5 * 1 + 4
    checks.append({
        'name': 'numerical_sanity_check',
        'passed': (val == 9),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'Computed 5*1+4 = {val}.',
    })

    # SymPy symbolic check that the substituted expression simplifies to 9.
    x_sym = symbols('x')
    f = 5 * x_sym + 4
    expr = f.subs(x_sym, 1)
    simplified = simplify(expr - 9)
    checks.append({
        'name': 'sympy_substitution_check',
        'passed': (simplified == 0),
        'backend': 'sympy',
        'proof_type': 'numerical',
        'details': f'Substitution gives {expr}; simplify(expr - 9) = {simplified}.',
    })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)