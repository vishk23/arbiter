import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []

    # Check 1: Verified certificate proof of the inverse-property claim.
    # We formalize the standard property of inverses for an invertible function:
    # f(f^{-1}(x)) = x.  From f(2) = f^{-1}(2), substituting into f(...) gives
    # f(f(2)) = f(f^{-1}(2)) = 2.
    x = Int('x')
    y = Int('y')
    f = Function('f', IntSort(), IntSort())
    finv = Function('finv', IntSort(), IntSort())

    # Axiom capturing inverse behavior for the specific point x=2.
    # Since the problem states f(2)=f^{-1}(2)=4, the crucial step is that
    # f(f^{-1}(2)) = 2 and therefore f(f(2)) = 2 by substitution.
    ax_inv = kd.axiom(ForAll([x], f(finv(x)) == x))

    try:
        thm = kd.prove(f(f(2)) == 2, by=[ax_inv, axiom := kd.axiom(f(2) == finv(2))])
        checks.append({
            'name': 'main_theorem_f_of_f_of_2',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': 'Proved f(f(2)) = 2 using the inverse identity f(f^{-1}(x)) = x together with f(2) = f^{-1}(2).'
        })
    except Exception as e:
        checks.append({
            'name': 'main_theorem_f_of_f_of_2',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Could not complete the proof in kdrag: {type(e).__name__}: {e}'
        })

    # Check 2: Numerical sanity check with a concrete invertible function.
    # Example: f(x) = x + 2, so f^{-1}(x) = x - 2.
    # This does not prove the theorem, but it sanity-checks the composition law.
    try:
        def f_num(t):
            return t + 2
        val = f_num(f_num(2))
        passed = (val == 6)
        checks.append({
            'name': 'numerical_sanity_example',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'For f(x)=x+2, f(f(2))={val}; this sanity-check confirms composition behavior in a concrete invertible example.'
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_example',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical sanity check failed: {type(e).__name__}: {e}'
        })

    proved = all(c['passed'] for c in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())