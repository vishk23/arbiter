import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Check 1: Fully verified theorem in kdrag/Z3.
    # We prove that any integer solution of the equation forces 3*x^2*y^2 = 588.
    x, y = Ints('x y')
    theorem = ForAll(
        [x, y],
        Implies(
            y*y + 3*x*x*y*y == 30*x*x + 517,
            3*x*x*y*y == 588,
        ),
    )
    try:
        prf = kd.prove(theorem)
        checks.append(
            {
                'name': 'main_diophantine_theorem',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove returned Proof object: {prf}',
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'main_diophantine_theorem',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kdrag proof failed: {type(e).__name__}: {e}',
            }
        )

    # Check 2: Symbolic sanity via exhaustive bounded search, confirming the unique integer solution.
    # This is not the primary proof, but it gives a concrete computational certificate of uniqueness
    # over a broad range and matches the derived exact solution.
    xi_vals = range(-100, 101)
    solutions = []
    for xi in xi_vals:
        rhs = 30 * xi * xi + 517
        denom = 1 + 3 * xi * xi
        if denom != 0 and rhs % denom == 0:
            yi2 = rhs // denom
            yi = int(sp.isqrt(yi2)) if hasattr(sp, 'isqrt') else int(sp.sqrt(yi2))
            if yi * yi == yi2:
                solutions.append((xi, yi))
                if yi != 0:
                    solutions.append((xi, -yi))
    # Remove duplicates from the above process and normalize.
    solutions = sorted(set(solutions))
    expected = sorted({(2, 7), (2, -7), (-2, 7), (-2, -7)})
    search_passed = set(solutions) == set(expected)
    if not search_passed:
        proved = False
    checks.append(
        {
            'name': 'bounded_integer_solution_search',
            'passed': search_passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Found solutions in [-100,100]: {solutions}; expected only x=±2, y=±7.',
        }
    )

    # Check 3: Numerical sanity check at the claimed solution.
    x0, y0 = 2, 7
    lhs = y0 * y0 + 3 * x0 * x0 * y0 * y0
    rhs = 30 * x0 * x0 + 517
    val = 3 * x0 * x0 * y0 * y0
    numerical_passed = (lhs == rhs) and (val == 588)
    if not numerical_passed:
        proved = False
    checks.append(
        {
            'name': 'numerical_sanity_at_claimed_solution',
            'passed': numerical_passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'At x=2, y=7: lhs={lhs}, rhs={rhs}, 3x^2y^2={val}.',
        }
    )

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)