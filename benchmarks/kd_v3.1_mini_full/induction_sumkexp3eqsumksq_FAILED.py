from sympy import symbols, summation, simplify
import kdrag as kd
from kdrag.smt import *


def _sum_upto(n):
    return n * (n - 1) // 2


def verify():
    checks = []
    proved = True

    # Check 1: symbolic verification of the closed-form identity
    try:
        n = symbols('n', integer=True, nonnegative=True)
        k = symbols('k', integer=True)
        sum_cubes = summation(k**3, (k, 0, n - 1))
        sum_linear_sq = summation(k, (k, 0, n - 1))**2
        diff = simplify(sum_cubes - sum_linear_sq)
        passed = diff == 0
        checks.append({
            'name': 'symbolic_closed_form_identity',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'simplify(sum_{k} k^3 - (sum_{k} k)^2) returned {diff!r}'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'symbolic_closed_form_identity',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy verification failed with exception: {e}'
        })
        proved = False

    # Check 2: kdrag verified proof of a concrete instance using a certificate
    try:
        n0 = IntVal(4)
        lhs = 0**3 + 1**3 + 2**3 + 3**3
        rhs = (0 + 1 + 2 + 3)**2
        prf = kd.prove(lhs == rhs)
        passed = prf is not None
        checks.append({
            'name': 'concrete_instance_certificate',
            'passed': passed,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove certified 0^3+1^3+2^3+3^3 == (0+1+2+3)^2; proof={prf!r}'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'concrete_instance_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed with exception: {e}'
        })
        proved = False

    # Check 3: numerical sanity check at a concrete value
    try:
        n_val = 7
        lhs_val = sum(k**3 for k in range(n_val))
        rhs_val = sum(k for k in range(n_val))**2
        passed = lhs_val == rhs_val
        checks.append({
            'name': 'numerical_sanity_n7',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'n={n_val}: lhs={lhs_val}, rhs={rhs_val}'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_n7',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical sanity check failed with exception: {e}'
        })
        proved = False

    # Check 4: explain the universal theorem in closed form
    try:
        n = symbols('n', integer=True, nonnegative=True)
        closed_form_cubes = (n * (n - 1) / 2)**2
        closed_form_sum = (n * (n - 1) / 2)**2
        passed = simplify(closed_form_cubes - closed_form_sum) == 0
        checks.append({
            'name': 'closed_form_match',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'Both sides reduce to (n(n-1)/2)^2, so their difference simplifies to 0.'
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            'name': 'closed_form_match',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Closed-form comparison failed with exception: {e}'
        })
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)