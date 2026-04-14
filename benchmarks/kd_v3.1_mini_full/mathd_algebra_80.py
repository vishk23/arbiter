import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: Certified algebraic proof with kdrag/Z3.
    x = Real('x')
    eq = (x - 9) / (x + 1) == 2
    theorem = Implies(And(eq, x != -1), x == -11)
    try:
        prf = kd.prove(ForAll([x], theorem))
        checks.append({
            'name': 'solve_rational_equation_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(prf),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'solve_rational_equation_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}',
        })

    # Check 2: Certify that x = -11 satisfies the equation and is not excluded.
    try:
        sat_thm = kd.prove(And(((-11) - 9) / ((-11) + 1) == 2, (-11) != -1))
        checks.append({
            'name': 'candidate_solution_validity',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(sat_thm),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'candidate_solution_validity',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'candidate verification failed: {e}',
        })

    # Check 3: Numerical sanity check at the claimed solution.
    try:
        lhs = ((-11) - 9) / (((-11) + 1))
        rhs = 2
        num_ok = abs(lhs - rhs) < 1e-12 and (-11) != -1
        checks.append({
            'name': 'numerical_sanity_at_minus_11',
            'passed': bool(num_ok),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'lhs={lhs}, rhs={rhs}, denominator_nonzero={(-11) != -1}',
        })
        if not num_ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_at_minus_11',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'numerical check failed: {e}',
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())