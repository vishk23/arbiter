import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof: encode the AMC condition in Z3/kdrag.
    a = Int('a')
    b = Int('b')
    # b is divisible by 10, and erasing its units digit gives a, so b = 10*a.
    thm_name = "sum_and_digit_erasure_implies_difference_14238"
    try:
        proof = kd.prove(
            ForAll([a, b],
                   Implies(And(a >= 0,
                               b >= 0,
                               a + b == 17402,
                               b == 10 * a),
                           b - a == 14238))
        )
        checks.append({
            'name': thm_name,
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned a proof object: {proof}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': thm_name,
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {type(e).__name__}: {e}'
        })

    # Symbolic verification with SymPy: solve 11x = 17402 exactly.
    try:
        x = sp.Symbol('x', integer=True, positive=True)
        sol = sp.solve(sp.Eq(11 * x, 17402), x)[0]
        answer = sp.simplify(10 * sol - sol)
        passed = (sol == 1582) and (answer == 14238)
        if not passed:
            proved = False
        checks.append({
            'name': 'sympy_solve_for_x_and_difference',
            'passed': bool(passed),
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'solve(11*x = 17402) gives x={sol}; difference 10*x - x = {answer}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_solve_for_x_and_difference',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'numerical',
            'details': f'SymPy computation failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check at the concrete values.
    try:
        x_val = 1582
        num1 = 10 * x_val
        num2 = x_val
        passed = (num1 + num2 == 17402) and (num1 - num2 == 14238) and (num1 % 10 == 0)
        if not passed:
            proved = False
        checks.append({
            'name': 'numerical_sanity_check_concrete_values',
            'passed': bool(passed),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numbers are {num1} and {num2}; sum={num1+num2}, difference={num1-num2}, divisible_by_10={num1%10==0}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check_concrete_values',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)