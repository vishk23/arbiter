from kdrag.smt import *
import kdrag as kd


def verify():
    checks = []
    proved = True

    # Variables for the puzzle
    A, B, C = Ints('A B C')

    # Main theorem: under the given constraints, A + B + C = 8.
    main_formula = ForAll(
        [A, B, C],
        Implies(
            And(
                A >= 1, A <= 9,
                B >= 1, B <= 9,
                C >= 1, C <= 9,
                A != B, A != C, B != C,
                A + B == C,
                (10*A + A) - B == 2*C,
                C * B == (10*A + A) + A,
            ),
            A + B + C == 8,
        ),
    )

    try:
        proof = kd.prove(main_formula)
        checks.append({
            'name': 'main_theorem_sum_is_8',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(proof),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'main_theorem_sum_is_8',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}',
        })

    # Derived intermediate lemma: from the first two equations, B = 3A.
    lemma1 = ForAll(
        [A, B, C],
        Implies(
            And(
                A >= 1, A <= 9,
                B >= 1, B <= 9,
                C >= 1, C <= 9,
                A + B == C,
                (10*A + A) - B == 2*C,
            ),
            B == 3*A,
        ),
    )
    try:
        proof1 = kd.prove(lemma1)
        checks.append({
            'name': 'lemma_B_equals_3A',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(proof1),
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'lemma_B_equals_3A',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}',
        })

    # Numerical sanity check using the unique solution A=1, B=3, C=4.
    a0, b0, c0 = 1, 3, 4
    numerical_ok = (
        a0 + b0 == c0 and
        (10*a0 + a0) - b0 == 2*c0 and
        c0 * b0 == (10*a0 + a0) + a0 and
        a0 + b0 + c0 == 8
    )
    checks.append({
        'name': 'numerical_sanity_unique_solution',
        'passed': numerical_ok,
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': 'Checked candidate solution A=1, B=3, C=4 satisfies all equations and sum 8.' if numerical_ok else 'Candidate solution failed numerical verification.',
    })
    if not numerical_ok:
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)