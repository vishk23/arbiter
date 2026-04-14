from sympy import symbols, Eq, solve
import kdrag as kd
from kdrag.smt import Ints, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof certificate via kdrag for the algebraic elimination step.
    try:
        x, w = Ints('x w')
        thm = kd.prove(
            ForAll([x, w], Implies(And(3 * x + 4 * w == 10, -2 * x - 3 * w == -4), x == 14))
        )
        checks.append({
            'name': 'elimination_proof_x_equals_14',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proved: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'elimination_proof_x_equals_14',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Check 2: Symbolic solve with SymPy confirms the unique solution has x = 14.
    try:
        x, y, z = symbols('x y z')
        sol = solve([
            Eq(3 * x + 4 * y - 12 * z, 10),
            Eq(-2 * x - 3 * y + 9 * z, -4)
        ], [x, y, z], dict=True)
        passed = bool(sol) and all(s.get(x) == 14 for s in sol)
        if not passed:
            proved = False
        checks.append({
            'name': 'sympy_linear_system_solution',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy solution set: {sol}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_linear_system_solution',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy solve failed: {type(e).__name__}: {e}'
        })

    # Check 3: Numerical sanity check at the claimed value x=14.
    try:
        x_val = 14
        # From the hint, w = y - 3z satisfies 3x + 4w = 10 and -2x - 3w = -4.
        # Solve numerically for w from the first equation.
        w_val = (10 - 3 * x_val) / 4
        lhs1 = 3 * x_val + 4 * w_val
        lhs2 = -2 * x_val - 3 * w_val
        passed = abs(lhs1 - 10) < 1e-12 and abs(lhs2 - (-4)) < 1e-12
        if not passed:
            proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'With x=14, w={(w_val):.6g}, equations evaluate to {lhs1:.6g} and {lhs2:.6g}.'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    import pprint
    pprint.pprint(verify())