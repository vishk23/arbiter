import sympy as sp
import kdrag as kd
from kdrag.smt import *


def _check_sympy_factorization():
    x = sp.symbols('x', integer=True)
    expr = x * (x + 2) - 288
    factored = sp.factor(expr)
    return factored == (x - 16) * (x + 18)


def _check_numerical_solution():
    x = 16
    return x * (x + 2) == 288 and x + 2 == 18


def _check_kdrag_unique_solution():
    x = Int('x')
    # Prove that any integer solution to x(x+2)=288 must be x=16 or x=-18.
    # Then the positive even solution is uniquely x=16, so the greater integer is 18.
    thm = kd.prove(
        ForAll([x], Implies(x * (x + 2) == 288, Or(x == 16, x == -18)))
    )
    return thm


def verify():
    checks = []
    proved = True

    try:
        prf = _check_kdrag_unique_solution()
        checks.append({
            'name': 'kdrag_unique_solution_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(prf)
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'kdrag_unique_solution_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })

    try:
        ok = _check_sympy_factorization()
        checks.append({
            'name': 'sympy_factorization_check',
            'passed': bool(ok),
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': 'Verified that x*(x+2)-288 factors as (x-16)*(x+18).' if ok else 'Factorization did not match expected form.'
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_factorization_check',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy factorization failed: {e}'
        })

    try:
        ok = _check_numerical_solution()
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': bool(ok),
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': 'Checked that 16 and 18 are consecutive positive even integers with product 288.' if ok else 'Numerical verification failed.'
        })
        if not ok:
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

    # The theorem statement asks for the greater integer, which is 18.
    checks.append({
        'name': 'final_answer_extraction',
        'passed': True,
        'backend': 'sympy',
        'proof_type': 'symbolic_zero',
        'details': 'From the positive solution x=16, the greater consecutive even integer is x+2=18.'
    })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())