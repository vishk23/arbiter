import kdrag as kd
from kdrag.smt import *
from sympy import symbols, expand, simplify


def verify():
    checks = []

    # Algebraic substitution a = x+y, b = x+z, c = y+z.
    x, y, z = symbols('x y z', real=True)
    a = x + y
    b = x + z
    c = y + z
    lhs = expand(a**2 * (b + c - a) + b**2 * (c + a - b) + c**2 * (a + b - c))
    rhs = expand(3 * a * b * c)
    diff = expand(rhs - lhs)
    target = expand(2 * (x + y + z) * (x*y + y*z + z*x) - 6*x*y*z)
    passed1 = simplify(diff - target) == 0
    checks.append({
        "name": "algebraic_reduction_under_substitution",
        "passed": bool(passed1),
    })

    # Z3-encodable auxiliary inequality:
    # For nonnegative x,y,z, (x+y+z)(xy+yz+zx) >= 9xyz.
    # This is not necessary for the main proof, but serves as a sanity check.
    xR, yR, zR = Real("xR"), Real("yR"), Real("zR")
    try:
        kd.prove(
            ForAll(
                [xR, yR, zR],
                Implies(
                    And(xR >= 0, yR >= 0, zR >= 0),
                    (xR + yR + zR) * (xR*yR + yR*zR + zR*xR) >= 9*xR*yR*zR,
                ),
            )
        )
        passed2 = True
    except kd.kernel.LemmaError:
        passed2 = False
    checks.append({
        "name": "auxiliary_am_gm_inequality",
        "passed": bool(passed2),
    })

    return checks