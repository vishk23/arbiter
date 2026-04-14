import kdrag as kd
from kdrag.smt import *
from kdrag.kernel import LemmaError
from sympy import Integer


def verify() -> dict:
    checks = []

    # Verified proof: use kdrag/Z3 to prove that the only integer solution is a=5, b=3,
    # hence b^a = 243.
    try:
        a, b = Ints('a b')
        thm = kd.prove(
            ForAll([a, b],
                   Implies(
                       And(a > 0, b > 0, 2**a == 32, a**b == 125),
                       b**a == 243
                   ))
        )
        checks.append({
            'name': 'z3_proof_b_to_the_a_equals_243',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {thm}'
        })
    except LemmaError as e:
        checks.append({
            'name': 'z3_proof_b_to_the_a_equals_243',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {e}'
        })

    # Symbolic sanity check using exact arithmetic in SymPy
    try:
        a_val = Integer(5)
        b_val = Integer(3)
        computed = b_val**a_val
        passed = computed == Integer(243)
        checks.append({
            'name': 'symbolic_exact_evaluation',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'Using a=5, b=3 gives b^a = {computed}.'
        })
    except Exception as e:
        checks.append({
            'name': 'symbolic_exact_evaluation',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'SymPy exact evaluation failed: {e}'
        })

    # Numerical sanity check at the concrete values from the hint.
    try:
        a_val = 5
        b_val = 3
        left1 = 2 ** a_val
        left2 = a_val ** b_val
        ans = b_val ** a_val
        passed = (left1 == 32) and (left2 == 125) and (ans == 243)
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Checked 2^5={left1}, 5^3={left2}, 3^5={ans}.'
        })
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })

    proved = all(ch['passed'] for ch in checks)
    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)