import kdrag as kd
from kdrag.smt import *
from kdrag.kernel import LemmaError


def _check_kdrag_proof():
    # Prove the two claimed solutions satisfy the divisibility condition.
    p, q, r = Ints('p q r')
    lhs = (p - 1) * (q - 1) * (r - 1)
    rhs = p * q * r - 1

    thm1 = kd.prove(And(p == 2, q == 4, r == 8, rhs % lhs == 0))
    thm2 = kd.prove(And(p == 3, q == 5, r == 15, rhs % lhs == 0))
    return thm1, thm2


def _check_numerical_sanity():
    # Direct arithmetic sanity check on the two solutions.
    sol1 = ((2 - 1) * (4 - 1) * (8 - 1), 2 * 4 * 8 - 1)
    sol2 = ((3 - 1) * (5 - 1) * (15 - 1), 3 * 5 * 15 - 1)
    return (sol1[1] % sol1[0] == 0) and (sol2[1] % sol2[0] == 0)


def verify():
    checks = []
    proved_all = True

    # Verified proof certificate: the stated solutions do satisfy the condition.
    try:
        thm1, thm2 = _check_kdrag_proof()
        checks.append({
            'name': 'candidate_solution_2_4_8_satisfies_divisibility',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm1),
        })
        checks.append({
            'name': 'candidate_solution_3_5_15_satisfies_divisibility',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm2),
        })
    except LemmaError as e:
        proved_all = False
        checks.append({
            'name': 'candidate_solution_2_4_8_satisfies_divisibility',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'proof failed: {e}',
        })
        checks.append({
            'name': 'candidate_solution_3_5_15_satisfies_divisibility',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'proof failed: {e}',
        })

    # Numerical sanity check.
    num_ok = _check_numerical_sanity()
    checks.append({
        'name': 'numerical_sanity_on_known_solutions',
        'passed': bool(num_ok),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': 'Checked by direct integer arithmetic on (2,4,8) and (3,5,15).',
    })
    proved_all = proved_all and num_ok

    # The uniqueness part of the IMO statement is not encoded here as a full formal proof,
    # because the provided backends do not include a complete search/induction framework
    # tailored to this olympiad proof. We therefore do not claim the full theorem proved.
    checks.append({
        'name': 'full_uniqueness_claim',
        'passed': False,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': 'Full uniqueness proof for all integer triples was not formalized in this module; only the candidate solutions were certified to satisfy the divisibility condition.',
    })
    proved_all = False

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    import json
    print(json.dumps(verify(), indent=2, default=str))