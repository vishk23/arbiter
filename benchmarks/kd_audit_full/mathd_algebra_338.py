from sympy import symbols
import kdrag as kd
from kdrag.smt import Ints, ForAll, Implies, And


def verify():
    checks = []

    # Verified proof: solve the linear system and prove abc = -56.
    try:
        a, b, c = Ints('a b c')
        premise = And(3*a + b + c == -3, a + 3*b + c == 9, a + b + 3*c == 19)
        thm = kd.prove(ForAll([a, b, c], Implies(premise, a*b*c == -56)))
        checks.append({
            'name': 'linear_system_implies_product',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm),
        })
    except Exception as e:
        checks.append({
            'name': 'linear_system_implies_product',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}',
        })

    # Numerical sanity check on the concrete solution.
    try:
        a0, b0, c0 = -4, 2, 7
        passed = (3*a0 + b0 + c0 == -3 and a0 + 3*b0 + c0 == 9 and a0 + b0 + 3*c0 == 19 and a0*b0*c0 == -56)
        checks.append({
            'name': 'numerical_sanity_check_solution',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Checked a={a0}, b={b0}, c={c0}; product={a0*b0*c0}.',
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check_solution',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}',
        })

    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)