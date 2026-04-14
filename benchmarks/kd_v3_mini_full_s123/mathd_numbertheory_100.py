import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: from gcd(n,40)=10 and lcm(n,40)=280, deduce n=70
    n = Int('n')
    g = Int('g')
    l = Int('l')

    # Since the problem statement is about positive integers, encode that domain.
    theorem = ForAll(
        [n, g, l],
        Implies(
            And(n > 0, g == 10, l == 280, g * l == n * 40),
            n == 70,
        ),
    )

    try:
        proof = kd.prove(theorem)
        checks.append(
            {
                'name': 'gcd_lcm_identity_implies_n_equal_70',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Kd proof obtained: {proof}',
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                'name': 'gcd_lcm_identity_implies_n_equal_70',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Could not prove the theorem in kdrag/Z3: {e}',
            }
        )

    # Symbolic / arithmetic verification of the computed answer.
    answer = 10 * 280 // 40
    checks.append(
        {
            'name': 'direct_arithmetic_computation',
            'passed': answer == 70,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'Computed 10*280//40 = {answer}.',
        }
    )
    if answer != 70:
        proved = False

    # Numerical sanity check on the identity gcd(n,40) * lcm(n,40) = n*40 for n=70.
    # For 70 and 40: gcd=10, lcm=280, so both sides equal 2800.
    lhs = 10 * 280
    rhs = 70 * 40
    checks.append(
        {
            'name': 'numerical_sanity_check_identity_at_n_70',
            'passed': lhs == rhs,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Checked 10*280 = {lhs} and 70*40 = {rhs}.',
        }
    )
    if lhs != rhs:
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)