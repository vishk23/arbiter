from kdrag.smt import *
import kdrag as kd


def _prove_affine_form():
    # Prove that any function satisfying the functional equation must be affine:
    # f(x) = 2x + c, where c = f(0).
    # We only encode the key consequence used in the intended solution:
    # from setting a = 0 we get f(f(b)) = c + 2 f(b), and by surjectivity of
    # the range of f onto its image, every value x in the image satisfies
    # f(x) = 2x + c.
    #
    # The full uniqueness statement for arbitrary functions Z -> Z is not
    # directly expressible as a single first-order Z3 theorem without an
    # explicit function symbol and axiomatization of surjectivity onto the image.
    # Instead, we verify the algebraic consistency of the proposed family and
    # a concrete numerical instance, and report the proof status honestly.
    x, a, b, c = Ints('x a b c')
    # Verified certificate: if f(t)=2t+c then the equation holds identically.
    # We encode the polynomial identity in the variables a,b,c.
    lhs = (2 * (2 * a) + c) + 2 * (2 * b + c)
    rhs = 2 * (2 * (a + b) + c) + c
    thm = kd.prove(ForAll([a, b, c], lhs == rhs))
    return thm


def verify():
    checks = []
    proved = True

    try:
        proof = _prove_affine_form()
        checks.append({
            'name': 'affine_family_satisfies_functional_equation',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Z3 certificate obtained: {proof}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'affine_family_satisfies_functional_equation',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check on a concrete instance.
    c0 = 7
    a0 = -3
    b0 = 5
    lhs_num = (2 * (2 * a0) + c0) + 2 * (2 * b0 + c0)
    rhs_num = 2 * (2 * (a0 + b0) + c0) + c0
    num_ok = (lhs_num == rhs_num)
    checks.append({
        'name': 'numerical_instance_check',
        'passed': bool(num_ok),
        'backend': 'numerical',
        'proof_type': 'numerical',
        'details': f'With c={c0}, a={a0}, b={b0}, lhs={lhs_num}, rhs={rhs_num}'
    })
    proved = proved and num_ok

    # Honest status for the full classification.
    checks.append({
        'name': 'full_classification_status',
        'passed': False,
        'backend': 'kdrag',
        'proof_type': 'certificate',
        'details': (
            'The module verifies the proposed family f(x)=2x+c satisfies the equation, '
            'but does not fully formalize the necessity direction (that every solution '
            'must be of this form) as a single kdrag theorem over arbitrary functions.'
        )
    })
    proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())