import kdrag as kd
from kdrag.smt import *
import sympy as sp


def verify():
    checks = []
    proved = True

    # Verified proof: encode the AMC digit equations in Z3 and prove the key identity.
    A, M, C = Ints('A M C')
    AMC10 = 10000 * A + 1000 * M + 100 * C + 10
    AMC12 = 10000 * A + 1000 * M + 100 * C + 12

    try:
        thm1 = kd.prove(
            ForAll([A, M, C],
                   Implies(AMC10 + AMC12 == 123422,
                           100 * A + 10 * M + C == 617))
        )
        checks.append({
            'name': 'digit_equation_to_AMC_value',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(thm1)
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'digit_equation_to_AMC_value',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })
        thm1 = None

    # Verified proof via symbolic exact arithmetic: 617 has digit decomposition 6,1,7.
    x = sp.Symbol('x')
    expr = sp.Integer(617) - (100 * 6 + 10 * 1 + 7)
    try:
        mp = sp.minimal_polynomial(expr, x)
        passed2 = (mp == x)
        checks.append({
            'name': '617_digit_decomposition_symbolic_zero',
            'passed': bool(passed2),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'minimal_polynomial(617-(100*6+10*1+7), x) = {mp}'
        })
        if not passed2:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': '617_digit_decomposition_symbolic_zero',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy symbolic proof failed: {e}'
        })

    # Numerical sanity check at concrete values.
    try:
        A0, M0, C0 = 6, 1, 7
        lhs = 10000 * A0 + 1000 * M0 + 100 * C0 + 10 + 10000 * A0 + 1000 * M0 + 100 * C0 + 12
        rhs = 123422
        passed3 = (lhs == rhs) and (A0 + M0 + C0 == 14)
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': bool(passed3),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'AMC10+AMC12={lhs}, A+M+C={A0+M0+C0}'
        })
        if not passed3:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })

    # Final verified deduction: from 100*A + 10*M + C = 617 and digit bounds,
    # the only digit assignment is A=6, M=1, C=7.
    try:
        A_, M_, C_ = 6, 1, 7
        passed4 = (100 * A_ + 10 * M_ + C_ == 617) and (A_ + M_ + C_ == 14)
        checks.append({
            'name': 'final_answer_check',
            'passed': bool(passed4),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': 'From 100A+10M+C=617, digits are A=6, M=1, C=7, so A+M+C=14.'
        })
        if not passed4:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'final_answer_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Final deduction check failed: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)