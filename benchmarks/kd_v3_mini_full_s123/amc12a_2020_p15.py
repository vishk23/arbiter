import sympy as sp
from sympy import symbols, Eq, Poly, factor, simplify, Abs, I, sqrt
from sympy import cos, pi, Rational, minimal_polynomial, Symbol

import kdrag as kd
from kdrag.smt import *


def _factorizations():
    z = symbols('z')
    p1 = z**3 - 8
    p2 = z**3 - 8*z**2 - 8*z + 64
    return sp.factor(p1), sp.factor(p2)


def _expected_roots():
    # A = roots of z^3 - 8 = 0
    # 8 = 2^3, so roots are 2 * cube roots of unity
    omega = -sp.Rational(1, 2) + sp.sqrt(3) * sp.I / 2
    A = [2, 2 * omega, 2 * omega**2]

    # B = roots of z^3 - 8z^2 - 8z + 64 = (z - 8)(z^2 - 8)
    B = [8, 2 * sp.sqrt(2), -2 * sp.sqrt(2)]
    return A, B


def _max_distance():
    A, B = _expected_roots()
    dists = [sp.simplify(sp.Abs(a - b)) for a in A for b in B]
    return sp.simplify(max(dists, key=lambda e: sp.N(e)))


def verify():
    checks = []

    z = symbols('z')
    f1, f2 = _factorizations()
    A, B = _expected_roots()

    # Polynomial factor checks
    ok1 = sp.expand(f1 - (z - 2) * (z**2 + 2*z + 4)) == 0
    ok2 = sp.expand(f2 - (z - 8) * (z**2 - 8)) == 0
    checks.append({
        'name': 'factorizations',
        'passed': bool(ok1 and ok2),
    })

    # Root-set checks by substitution
    p1 = z**3 - 8
    p2 = z**3 - 8*z**2 - 8*z + 64
    ok_roots = all(sp.simplify(p1.subs(z, a)) == 0 for a in A) and all(sp.simplify(p2.subs(z, b)) == 0 for b in B)
    checks.append({
        'name': 'roots_satisfy_polynomials',
        'passed': bool(ok_roots),
    })

    # Distance computation: the maximum is between 2 and -2*sqrt(2)
    maxd = _max_distance()
    ok_dist = sp.simplify(maxd - 2*sp.sqrt(21)) == 0
    checks.append({
        'name': 'maximum_distance',
        'passed': bool(ok_dist),
    })

    return {
        'proved': all(c['passed'] for c in checks),
        'checks': checks,
        'answer': str(maxd),
    }


if __name__ == '__main__':
    print(verify())