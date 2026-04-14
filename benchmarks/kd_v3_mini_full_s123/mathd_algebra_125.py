import kdrag as kd
from kdrag.smt import *
from sympy import symbols, Eq, solve


def verify():
    checks = []
    proved = True

    # Verified proof: formal derivation in Z3/kdrag
    x = Int('x')
    y = Int('y')
    thm = None
    try:
        thm = kd.prove(
            ForAll([x, y],
                   Implies(And(y == 5 * x, (x - 3) + (y - 3) == 30), x == 6))
        )
        checks.append({
            'name': 'formal_age_equation_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'formal_age_equation_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {type(e).__name__}: {e}'
        })

    # SymPy symbolic sanity check: solve the equation exactly
    try:
        xs = symbols('x')
        sol = solve(Eq((xs - 3) + (5 * xs - 3), 30), xs)
        passed = (sol == [6]) or (sol == (6,)) or (len(sol) == 1 and sol[0] == 6)
        checks.append({
            'name': 'sympy_solve_sanity',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'solve(Eq((x-3)+(5x-3),30), x) -> {sol}'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_solve_sanity',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'SymPy solve failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check at the claimed answer x=6, y=30
    try:
        x_val = 6
        y_val = 5 * x_val
        eq1 = (y_val == 5 * x_val)
        eq2 = ((x_val - 3) + (y_val - 3) == 30)
        passed = bool(eq1 and eq2)
        checks.append({
            'name': 'numerical_substitution_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'substitute x=6, y=30 -> age relation {eq1}, sum relation {eq2}'
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_substitution_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    import pprint
    pprint.pprint(verify())