from itertools import product

import kdrag as kd
from kdrag.smt import *


def _pow_mod(base, exp, mod):
    r = 1 % mod
    b = base % mod
    e = exp
    while e > 0:
        if e & 1:
            r = (r * b) % mod
        b = (b * b) % mod
        e >>= 1
    return r


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof by exhaustive modular residues.
    # For every residue class mod 11, x^5 is in {0,1,10} and y^2+4 is in {2,4,5,7,8,9};
    # these sets are disjoint, so equality is impossible modulo 11.
    try:
        x = Int('x')
        y = Int('y')
        mod = 11

        bad_pairs = []
        for rx, ry in product(range(mod), repeat=2):
            lhs = _pow_mod(rx, 5, mod)
            rhs = (ry * ry + 4) % mod
            if lhs == rhs:
                bad_pairs.append((rx, ry, lhs, rhs))

        if bad_pairs:
            checks.append({
                'name': 'mod_11_residue_separation',
                'passed': False,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'Found residue collisions modulo 11: {bad_pairs[:5]}',
            })
            proved = False
        else:
            # Encode the contradiction as a Z3-provable universally quantified statement.
            # If x^5 == y^2 + 4, then their residues mod 11 would be equal; but exhaustive
            # residue checking shows this never happens.
            thm = kd.prove(ForAll([x, y], x**5 != y**2 + 4), by=[])
            checks.append({
                'name': 'mod_11_residue_separation',
                'passed': True,
                'backend': 'kdrag',
                'proof_type': 'certificate',
                'details': f'kd.prove returned certificate: {thm}',
            })
    except Exception as e:
        checks.append({
            'name': 'mod_11_residue_separation',
            'passed': False,
            'backend': 'kdrag',
            'proof_type': 'certificate',
            'details': f'Proof attempt failed: {type(e).__name__}: {e}',
        })
        proved = False

    # Check 2: Numerical sanity check at concrete values.
    try:
        sample_x, sample_y = 2, 3
        lhs = sample_x**5
        rhs = sample_y**2 + 4
        passed = lhs != rhs
        checks.append({
            'name': 'numerical_sanity_sample',
            'passed': passed,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'x={sample_x}, y={sample_y}: x^5={lhs}, y^2+4={rhs}, unequal={passed}',
        })
        if not passed:
            proved = False
    except Exception as e:
        checks.append({
            'name': 'numerical_sanity_sample',
            'passed': False,
            'backend': 'numerical',
            'proof_type': 'numerical',
            'details': f'Numerical check failed: {type(e).__name__}: {e}',
        })
        proved = False

    return {'proved': proved, 'checks': checks}


if __name__ == '__main__':
    result = verify()
    print(result)