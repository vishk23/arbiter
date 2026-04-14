import kdrag as kd
from kdrag.smt import *
import sympy as sp


def _linear_sum_proof():
    x, y, z = Ints('x y z')
    # If the three equations hold, then their sum gives 6(x+y+z)=72, hence x+y+z=12.
    thm = kd.prove(
        ForAll(
            [x, y, z],
            Implies(
                And(3 * x + y == 17, 5 * y + z == 14, 3 * x + 5 * z == 41),
                x + y + z == 12,
            ),
        )
    )
    return thm


def _sympy_solve_check():
    x, y, z = sp.symbols('x y z')
    sol = sp.solve(
        [sp.Eq(3 * x + y, 17), sp.Eq(5 * y + z, 14), sp.Eq(3 * x + 5 * z, 41)],
        [x, y, z],
        dict=True,
    )
    if not sol:
        return False, 'SymPy returned no solution.'
    s = sp.simplify(sol[0][x] + sol[0][y] + sol[0][z])
    return bool(s == 12), f'SymPy solved the system and obtained x+y+z = {s}.'


def _numerical_sanity_check():
    # The system has the unique solution x=4, y=5, z=-11.
    x, y, z = 4, 5, -11
    ok = (3 * x + y == 17) and (5 * y + z == 14) and (3 * x + 5 * z == 41) and (x + y + z == 12)
    return ok, f'Checked candidate solution (x, y, z)=({x}, {y}, {z}); sum is {x+y+z}.'


def verify():
    checks = []
    proved = True

    # Verified certificate proof using kdrag/Z3.
    try:
        cert = _linear_sum_proof()
        checks.append(
            {
                'name': 'kdrag_linear_sum_certificate',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove succeeded: {cert}',
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'kdrag_linear_sum_certificate',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove failed: {type(e).__name__}: {e}',
            }
        )

    sympy_ok, sympy_details = _sympy_solve_check()
    checks.append(
        {
            'name': 'sympy_linear_system_solution',
            'passed': sympy_ok,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': sympy_details,
        }
    )
    proved = proved and sympy_ok

    num_ok, num_details = _numerical_sanity_check()
    checks.append(
        {
            'name': 'numerical_sanity_check',
            'passed': num_ok,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': num_details,
        }
    )
    proved = proved and num_ok

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())