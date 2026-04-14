from kdrag.smt import *
import kdrag as kd


def verify():
    checks = []
    proved = True

    half = RealVal(1) / 2

    # Check 1: formal proof of the core algebraic identity.
    t = Real('t')
    core_formula = ForAll([t], (half - t) * (half - t) == (t - half) * (t - half))
    try:
        p1 = kd.prove(core_formula)
        checks.append({
            'name': 'square_symmetry_certificate',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(p1)
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'square_symmetry_certificate',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}'
        })

    # Check 2: symbolic verification of the algebraic step.
    u = Real('u')
    identity_formula = ForAll([u], half + (half - u) == u)
    try:
        p2 = kd.prove(identity_formula)
        checks.append({
            'name': 'iterate_returns_original_value',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(p2)
        })
    except Exception as e:
        proved = False
        checks.append({
            'name': 'iterate_returns_original_value',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof failed: {e}'
        })

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    print(verify())