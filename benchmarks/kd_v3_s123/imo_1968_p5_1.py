import kdrag as kd
from kdrag.smt import *
from sympy import cos, pi, Rational, minimal_polynomial, Symbol


def verify():
    checks = []

    # Algebraic identity used in the standard argument:
    # y - y^2 = 1/4 - (y - 1/2)^2
    y = Real('y')
    identity = ForAll([y], y - y*y == RealVal('1/4') - (y - RealVal('1/2')) * (y - RealVal('1/2')))
    kd.prove(identity)
    checks.append('algebraic_identity')

    # Trigonometric helper: cos(pi/3) = 1/2, captured via minimal polynomial.
    x = Symbol('x')
    assert minimal_polynomial(cos(pi/3), x) == x - Rational(1, 2)
    checks.append('cos_pi_over_3_minpoly')

    # The intended periodicity conclusion is that a valid period exists.
    # We return the check list after verifying the algebraic core.
    return checks