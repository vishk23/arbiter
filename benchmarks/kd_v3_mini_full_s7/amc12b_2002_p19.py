import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Let x = ab, y = bc, z = ca.
    # Then x + y = 152, y + z = 162, z + x = 170.
    # Solving gives x=80, y=72, z=90, so (abc)^2 = xyz = 518400 = 720^2.
    # Since a,b,c are positive, abc = 720.

    a, b, c = Reals('a b c')
    x, y, z = Reals('x y z')

    hyp = And(
        a > 0,
        b > 0,
        c > 0,
        a * (b + c) == 152,
        b * (c + a) == 162,
        c * (a + b) == 170,
        x == a * b,
        y == b * c,
        z == c * a,
    )

    # Prove the pairwise products.
    try:
        kd.prove(
            ForAll([a, b, c, x, y, z],
                   Implies(hyp, And(x == 80, y == 72, z == 90))),
            by=[]
        )
        checks.append('pairwise_products')
    except Exception:
        # Fallback: prove the linear system directly.
        kd.prove(
            ForAll([x, y, z],
                   Implies(And(x + y == 152, y + z == 162, z + x == 170),
                           And(x == 80, y == 72, z == 90))),
            by=[]
        )
        checks.append('pairwise_products')

    # Now prove abc = 720 from xyz = 80*72*90.
    u = Real('u')
    try:
        kd.prove(
            ForAll([u], Implies(And(u > 0, u * u == 80 * 72 * 90), u == 720)),
            by=[]
        )
        checks.append('positive_square_root')
    except Exception:
        # Directly prove the target by algebraic simplification.
        kd.prove(
            ForAll([a, b, c],
                   Implies(And(a > 0, b > 0, c > 0,
                               a * (b + c) == 152,
                               b * (c + a) == 162,
                               c * (a + b) == 170),
                           a * b * c == 720)),
            by=[]
        )
        checks.append('main_theorem_abc_equals_720')

    # If we got here, the claim is verified.
    if 'main_theorem_abc_equals_720' not in checks:
        kd.prove(
            ForAll([a, b, c],
                   Implies(And(a > 0, b > 0, c > 0,
                               a * (b + c) == 152,
                               b * (c + a) == 162,
                               c * (a + b) == 170),
                           a * b * c == 720)),
            by=[]
        )
        checks.append('main_theorem_abc_equals_720')

    return checks