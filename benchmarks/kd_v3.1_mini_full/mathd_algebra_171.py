from sympy import symbols, simplify
import kdrag as kd
from kdrag.smt import Int, ForAll, Implies


def verify():
    checks = []
    proved = True

    # Verified proof: the expression 5*1 + 4 equals 9.
    try:
        x = Int('x')
        thm = kd.prove(5 * 1 + 4 == 9)
        checks.append({
            'name': 'f(1) equals 9 via kdrag proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm)
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'f(1) equals 9 via kdrag proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    # Symbolic verification with SymPy substitution.
    try:
        x = symbols('x')
        f = 5 * x + 4
        f1 = simplify(f.subs(x, 1))
        passed = (f1 == 9)
        if not passed:
            proved = False
        checks.append({
            'name': 'SymPy substitution check',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'f(1) simplifies to {f1}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'SymPy substitution check',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy check failed: {e}'
        })

    # Numerical sanity check.
    try:
        numeric_val = 5 * 1 + 4
        passed = (numeric_val == 9)
        if not passed:
            proved = False
        checks.append({
            'name': 'Numerical sanity check at x=1',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Computed 5*1+4 = {numeric_val}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'Numerical sanity check at x=1',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())