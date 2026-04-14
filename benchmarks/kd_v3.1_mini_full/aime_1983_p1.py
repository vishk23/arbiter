from sympy import symbols, Eq, solve, Rational
import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    # Check 1: Verified proof via kdrag (certificate object)
    try:
        a = Real('a')
        # Encode the logarithm relations in terms of ln values.
        # Let lnx = a/24, lny = a/40, lnxyz = a/12, so ln z = a/60.
        lnx = a / 24
        lny = a / 40
        lnxyz = a / 12
        lnz = lnxyz - lnx - lny
        thm = kd.prove(ForAll([a], Implies(a != 0, a / lnz == 60)))
        checks.append({
            'name': 'logarithm_relation_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove succeeded: {thm}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'logarithm_relation_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove failed: {type(e).__name__}: {e}'
        })

    # Check 2: SymPy symbolic derivation of the value 60
    try:
        a = symbols('a', nonzero=True)
        lnx = a / 24
        lny = a / 40
        lnxyz = a / 12
        lnz = lnxyz - lnx - lny
        expr = (a / lnz).simplify()
        passed = bool(expr == 60)
        if not passed:
            proved = False
        checks.append({
            'name': 'sympy_change_of_base',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'simplified expression = {expr}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'sympy_change_of_base',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy derivation failed: {type(e).__name__}: {e}'
        })

    # Check 3: Numerical sanity check with concrete values
    try:
        import math
        a_val = 120.0
        lnx = a_val / 24.0
        lny = a_val / 40.0
        lnxyz = a_val / 12.0
        lnz = lnxyz - lnx - lny
        numeric = a_val / lnz
        passed = abs(numeric - 60.0) < 1e-12
        if not passed:
            proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'with a=120, computed log_z(w) = {numeric}'
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)