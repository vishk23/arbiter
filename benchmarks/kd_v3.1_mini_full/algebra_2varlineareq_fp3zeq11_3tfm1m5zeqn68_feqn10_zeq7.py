import kdrag as kd
from kdrag.smt import Ints, And, Implies


def verify():
    checks = []

    f, z = Ints('f z')

    # Verified proof: the linear system implies f = -10 and z = 7.
    # Encode the arithmetic consequence directly in Z3 and obtain a proof certificate.
    theorem = kd.prove(
        Implies(
            And(f + 3 * z == 11, 3 * (f - 1) - 5 * z == -68),
            And(f == -10, z == 7),
        )
    )
    checks.append(
        {
            'name': 'linear_system_implies_unique_solution',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {theorem}',
        }
    )

    # Numerical sanity check at the claimed solution.
    f0, z0 = -10, 7
    eq1 = (f0 + 3 * z0 == 11)
    eq2 = (3 * (f0 - 1) - 5 * z0 == -68)
    checks.append(
        {
            'name': 'numerical_sanity_check_claimed_values',
            'passed': bool(eq1 and eq2),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'At f={f0}, z={z0}: equation1={eq1}, equation2={eq2}.',
        }
    )

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)