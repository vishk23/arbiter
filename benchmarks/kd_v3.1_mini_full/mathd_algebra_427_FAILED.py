import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof: encode the linear equations over integers and prove the sum.
    x, y, z, s = Ints('x y z s')
    assumptions = And(3 * x + y == 17, 5 * y + z == 14, 3 * x + 5 * z == 41, s == x + y + z)
    goal = s == 12
    try:
        thm = kd.prove(ForAll([x, y, z, s], Implies(assumptions, goal)))
        checks.append({
            'name': 'linear_system_sum_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'linear_system_sum_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Failed to prove the universal implication: {e}',
        })

    # SymPy symbolic verification: solve the system and compute the sum.
    try:
        sx, sy, sz = sp.symbols('x y z')
        sol = sp.solve([
            sp.Eq(3 * sx + sy, 17),
            sp.Eq(5 * sy + sz, 14),
            sp.Eq(3 * sx + 5 * sz, 41),
        ], [sx, sy, sz], dict=True)
        if not sol:
            raise ValueError('SymPy returned no solutions')
        sol0 = sol[0]
        ans = sp.simplify(sol0[sx] + sol0[sy] + sol0[sz])
        passed = (ans == 12)
        if not passed:
            proved = False
        checks.append({
            'name': 'sympy_solve_and_sum',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'solution={sol0}, sum={ans}',
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_solve_and_sum',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy verification failed: {e}',
        })

    # Numerical sanity check at the concrete solution (4,5,3).
    try:
        xv, yv, zv = 4, 5, 3
        eq1 = (3 * xv + yv == 17)
        eq2 = (5 * yv + zv == 14)
        eq3 = (3 * xv + 5 * zv == 41)
        sum_ok = (xv + yv + zv == 12)
        passed = eq1 and eq2 and eq3 and sum_ok
        if not passed:
            proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'(x,y,z)=({xv},{yv},{zv}), equations=({eq1},{eq2},{eq3}), sum={xv+yv+zv}',
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}',
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())