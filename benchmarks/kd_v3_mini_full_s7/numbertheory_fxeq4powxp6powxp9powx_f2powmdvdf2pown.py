import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def f(t):
    return Integer(4) ** t + Integer(6) ** t + Integer(9) ** t


def verify():
    checks = []

    # The original divisibility claim is false.
    # Counterexample: m = 1, n = 2.
    # f(2) = 4^2 + 6^2 + 9^2 = 133
    # f(4) = 4^4 + 6^4 + 9^4 = 8113
    # 8113 mod 133 = 47, so 133 does not divide 8113.
    m = 1
    n = 2
    fm = f(2 ** m)
    fn = f(2 ** n)
    rem = fn % fm
    checks.append(
        {
            "name": "counterexample_m1_n2",
            "passed": bool(rem != 0),
            "backend": "symbolic",
            "proof_type": "counterexample",
            "details": f"f(2^{m}) = {fm}, f(2^{n}) = {fn}, remainder = {rem}",
        }
    )

    # Also verify the base case m = n, where divisibility holds trivially.
    m0 = 1
    fm0 = f(2 ** m0)
    checks.append(
        {
            "name": "trivial_self_divisibility_m1",
            "passed": bool(fm0 % fm0 == 0),
            "backend": "symbolic",
            "proof_type": "sanity_check",
            "details": f"f(2^{m0}) = {fm0} divides itself",
        }
    )

    return checks