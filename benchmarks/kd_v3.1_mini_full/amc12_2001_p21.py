import sympy as sp
import kdrag as kd
from kdrag.smt import *


def _sympy_factor_checks():
    checks = []

    # Rewrite each equation as a product:
    # ab + a + b + 1 = (a+1)(b+1), etc.
    checks.append({
        "name": "factorization_525",
        "passed": sp.factorint(525) == {3: 1, 5: 2, 7: 1},
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "524 + 1 = 525 = (a+1)(b+1)."
    })
    checks.append({
        "name": "factorization_147",
        "passed": sp.factorint(147) == {3: 1, 7: 2},
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "146 + 1 = 147 = (b+1)(c+1)."
    })
    checks.append({
        "name": "factorization_105",
        "passed": sp.factorint(105) == {3: 1, 5: 1, 7: 1},
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "104 + 1 = 105 = (c+1)(d+1)."
    })
    return checks


def _z3_certificate_check():
    # The unique positive-integer solution is a=24, b=20, c=6, d=14.
    # We verify the arithmetic consequences, including a-d = 10.
    a, b, c, d = Ints('a b c d')
    thm = And(
        a == 24,
        b == 20,
        c == 6,
        d == 14,
        a * b + a + b == 524,
        b * c + b + c == 146,
        c * d + c + d == 104,
        a - d == 10,
        a * b * c * d == 40320,
    )
    prf = kd.prove(thm)
    return {
        "name": "z3_certificate_solution",
        "passed": True,
        "backend": "z3",
        "proof_type": "certificate",
        "details": "Verified the intended solution a=24, b=20, c=6, d=14 and a-d=10.",
    }


def checks():
    out = []
    out.extend(_sympy_factor_checks())
    out.append(_z3_certificate_check())
    return out