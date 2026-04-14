import kdrag as kd
from kdrag.smt import *
from sympy import cos, pi, Rational, minimal_polynomial, Symbol


def verify():
    checks = []

    # Check 1: the proposed solutions satisfy the divisibility condition.
    # (2, 4, 8)
    lhs1 = (2 - 1) * (4 - 1) * (8 - 1)
    rhs1 = 2 * 4 * 8 - 1
    assert rhs1 % lhs1 == 0
    checks.append("(2,4,8) satisfies the divisibility condition.")

    # (3, 5, 15)
    lhs2 = (3 - 1) * (5 - 1) * (15 - 1)
    rhs2 = 3 * 5 * 15 - 1
    assert rhs2 % lhs2 == 0
    checks.append("(3,5,15) satisfies the divisibility condition.")

    return checks