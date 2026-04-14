import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Model the inverse relationship explicitly with a function g = f^{-1}.
    x = Int('x')
    f = Function('f', IntSort(), IntSort())
    g = Function('g', IntSort(), IntSort())

    inv_left = ForAll([x], f(g(x)) == x)
    inv_right = ForAll([x], g(f(x)) == x)

    # Given facts from the problem.
    h_f2 = f(2) == 4
    h_g2 = g(2) == 4

    # Main theorem: under the assumptions, f(f(2)) = 2.
    goal = Implies(And(inv_left, inv_right, h_f2, h_g2), f(f(2)) == 2)

    try:
        prf = kd.prove(goal)
        checks.append({
            'name': 'main_inverse_function_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(prf),
        })
    except Exception as e:
        checks.append({
            'name': 'main_inverse_function_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof attempt failed: {type(e).__name__}: {e}',
        })

    # Additional certified consistency check: if f(2)=4 and g is the inverse,
    # then f(g(2)) = 2, and since g(2)=4, this forces f(4)=2.
    certified_step = Implies(And(inv_left, h_g2), f(4) == 2)
    try:
        prf2 = kd.prove(certified_step)
        checks.append({
            'name': 'derived_f4_equals_2',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(prf2),
        })
    except Exception as e:
        checks.append({
            'name': 'derived_f4_equals_2',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof attempt failed: {type(e).__name__}: {e}',
        })

    # Numerical sanity check on a concrete invertible function: f(x)=x+2, g(x)=x-2.
    # This is only a sanity check, not the primary proof.
    try:
        def f_num(t):
            return t + 2
        def g_num(t):
            return t - 2
        passed = (f_num(2) == 4) and (g_num(2) == 0) and (f_num(f_num(2)) == 6)
        # Note: this sanity check is just to show the checker mechanism; it does
        # not model the problem's hypotheses, so we report it as a numerical check.
        checks.append({
            'name': 'numerical_sanity_example',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': 'Sanity check on a concrete invertible function example (not a proof of the theorem).',
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_example',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical sanity check failed: {type(e).__name__}: {e}',
        })

    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)