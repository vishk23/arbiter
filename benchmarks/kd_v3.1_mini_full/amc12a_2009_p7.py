from sympy import Symbol, Eq, solve
import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify():
    checks = []
    proved_all = True

    # Check 1: Verify the arithmetic-sequence condition forces x = 4.
    try:
        x = Int('x')
        # Constant difference condition:
        # (5x - 11) - (2x - 3) = (3x + 1) - (5x - 11)
        thm_x = kd.prove(
            ForAll([x], Implies(
                And((5*x - 11) - (2*x - 3) == (3*x + 1) - (5*x - 11), True),
                x == 4
            ))
        )
        passed = True
        details = f'kd.prove returned certificate: {thm_x}'
    except Exception as e:
        passed = False
        proved_all = False
        details = f'Failed to prove x=4 from equal differences: {e}'
    checks.append({
        'name': 'constant_difference_implies_x_equals_4',
        'passed': passed,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': details,
    })

    # Check 2: Symbolic verification of the nth term formula and n = 502.
    try:
        n = Int('n')
        # From x=4, sequence terms are 5, 9, 13, so common difference is 4 and term_n = 1 + 4n.
        thm_n = kd.prove(
            ForAll([n], Implies(1 + 4*n == 2009, n == 502))
        )
        passed = True
        details = f'kd.prove returned certificate: {thm_n}'
    except Exception as e:
        passed = False
        proved_all = False
        details = f'Failed to prove 1+4n=2009 implies n=502: {e}'
    checks.append({
        'name': 'solve_for_n_equals_502',
        'passed': passed,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': details,
    })

    # Check 3: Numerical sanity check using the derived formula at n=502.
    try:
        value = 1 + 4 * 502
        passed = (value == 2009)
        details = f'Computed 1 + 4*502 = {value}; expected 2009.'
    except Exception as e:
        passed = False
        proved_all = False
        details = f'Numerical sanity check failed: {e}'
    checks.append({
        'name': 'numerical_sanity_check_term_502',
        'passed': passed,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': details,
    })

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    print(verify())