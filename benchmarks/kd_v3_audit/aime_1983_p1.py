import kdrag as kd
from kdrag.smt import *
import sympy as sp


def _proof_main():
    # Variables: logarithms are represented by real numbers.
    lx, ly, lz, lw = Reals('lx ly lz lw')
    # We use natural logs as a convenient representation.
    # Let lx = ln x, etc. Then the given facts imply:
    # lw/lx = 24, lw/ly = 40, lw/(lx+ly+lz) = 12.
    # From these, we prove lz = lw/60, hence log_z(w)=60.

    # The theorem is encoded as an existential-free arithmetic identity.
    thm = ForAll([lw], Implies(lw > 0,
        Exists([lx, ly, lz], And(
            lx == lw/24,
            ly == lw/40,
            lx + ly + lz == lw/12,
            lz == lw/60
        ))
    ))
    # This is a certificate-style proof attempt for the algebraic core.
    return kd.prove(thm)


def verify():
    checks = []
    all_passed = True

    # Check 1: symbolic algebraic derivation with SymPy (rigorous exact arithmetic).
    try:
        a = sp.symbols('a', positive=True)
        lnz = a/sp.Integer(12) - a/sp.Integer(24) - a/sp.Integer(40)
        ans = sp.simplify(a/lnz)
        passed = (ans == 60)
        checks.append({
            'name': 'sympy_exact_log_derivation',
            'passed': passed,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'simplify(a / (a/12 - a/24 - a/40)) -> {ans}'
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            'name': 'sympy_exact_log_derivation',
            'passed': False,
            'backend': 'sympy',
            'proof_type': 'symbolic_zero',
            'details': f'SymPy failed: {e}'
        })
        all_passed = False

    # Check 2: numerical sanity check at a concrete value.
    try:
        a_val = 5.0
        lnz_val = a_val/12.0 - a_val/24.0 - a_val/40.0
        ans_val = a_val/lnz_val
        passed = abs(ans_val - 60.0) < 1e-12
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'With a=5, computed log_z(w) = {ans_val}'
        })
        all_passed = all_passed and passed
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_check',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {e}'
        })
        all_passed = False

    # Check 3: verified kdrag proof of the core arithmetic identity.
    # From 1/12 - 1/24 - 1/40 = 1/60.
    try:
        q = Real('q')
        thm = ForAll([q], Implies(q > 0, q/12 - q/24 - q/40 == q/60))
        proof = kd.prove(thm)
        checks.append({
            'name': 'kdrag_rational_identity_proof',
            'passed': True,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': str(proof)
        })
        all_passed = all_passed and True
    except Exception as e:
        checks.append({
            'name': 'kdrag_rational_identity_proof',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'kdrag proof failed: {e}'
        })
        all_passed = False

    return {'proved': all_passed, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)