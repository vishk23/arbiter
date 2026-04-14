import kdrag as kd
from kdrag.smt import *
from sympy import mod_inverse


def verify():
    checks = []
    proved_all = True

    # Verified proof: 160 * 1058 == 1 mod 1399
    try:
        n = Int('n')
        thm = kd.prove((160 * 1058) % 1399 == 1)
        checks.append({
            'name': 'kdrag_inverse_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kd.prove returned proof: {thm}'
        })
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'kdrag_inverse_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof attempt failed: {type(e).__name__}: {e}'
        })

    # SymPy exact computation check
    try:
        inv = mod_inverse(160, 1399)
        passed = (inv == 1058)
        checks.append({
            'name': 'sympy_mod_inverse_value',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'mod_inverse(160, 1399) = {inv}; expected 1058'
        })
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'sympy_mod_inverse_value',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'Computation failed: {type(e).__name__}: {e}'
        })

    # Numerical sanity check
    try:
        lhs = (160 * 1058) % 1399
        passed = (lhs == 1)
        checks.append({
            'name': 'numerical_sanity_modulo',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'(160 * 1058) % 1399 = {lhs}, expected 1'
        })
        if not passed:
            proved_all = False
    except Exception as e:
        proved_all = False
        checks.append({
            'name': 'numerical_sanity_modulo',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Computation failed: {type(e).__name__}: {e}'
        })

    return {'proved': proved_all, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)