import sympy as sp
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: Verified symbolic proof via kdrag for the core algebraic consequence.
    # Let y = -6 and assume x is negative. From distance 15 to (8,3):
    # (x-8)^2 + (y-3)^2 = 225, so (x-8)^2 + 81 = 225, hence (x-8)^2 = 144.
    # With x < 0, the only possible root is x = -4, and then x^2 + y^2 = 52.
    x = Real('x')
    y = Real('y')
    thm = None
    try:
        thm = kd.prove(
            ForAll([x, y],
                   Implies(
                       And(y == -6,
                           x < 0,
                           (x - 8) * (x - 8) + (y - 3) * (y - 3) == 15 * 15),
                       x * x + y * y == 52
                   )))
        checks.append({
            'name': 'core_distance_equations_imply_n_equals_52',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof object obtained: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'core_distance_equations_imply_n_equals_52',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}'
        })

    # Check 2: SymPy symbolic verification of the quadratic root selection.
    try:
        xs = sp.symbols('xs', real=True)
        sol_x = sp.solve((xs - 8)**2 + (-6 - 3)**2 - 15**2, xs)
        neg_roots = [s for s in sol_x if sp.simplify(s < 0)]
        x_val = neg_roots[0]
        n_val = sp.simplify(x_val**2 + (-6)**2)
        passed = sp.simplify(n_val - 52) == 0
        checks.append({
            'name': 'symbolic_root_selection_and_n_value',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'solutions={sol_x}, chosen_negative_root={x_val}, n={n_val}'
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            'name': 'symbolic_root_selection_and_n_value',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy verification failed: {type(e).__name__}: {e}'
        })

    # Check 3: Numerical sanity check at the concrete point (-4, -6).
    try:
        x0, y0 = -4, -6
        dist_to_x_axis = abs(y0)
        dist_to_point = ((x0 - 8)**2 + (y0 - 3)**2) ** 0.5
        dist_to_origin_sq = x0**2 + y0**2
        passed = (dist_to_x_axis == 6 and abs(dist_to_point - 15) < 1e-12 and dist_to_origin_sq == 52)
        checks.append({
            'name': 'numerical_sanity_at_minus4_minus6',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'dist_to_x_axis={dist_to_x_axis}, dist_to_point={dist_to_point}, dist_to_origin_sq={dist_to_origin_sq}'
        })
        proved = proved and bool(passed)
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_at_minus4_minus6',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())