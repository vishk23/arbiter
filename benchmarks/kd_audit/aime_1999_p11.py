from sympy import Symbol, Rational, pi, sin, cos, tan, simplify, trigsimp, minimal_polynomial, N

# Attempt to use Knuckledragger if available; otherwise keep verification symbolic/numerical.
try:
    import kdrag as kd
    from kdrag.smt import *
    _KDRAG_AVAILABLE = True
except Exception:
    kd = None
    _KDRAG_AVAILABLE = False


def _sympy_trig_identity_check():
    # Prove the exact trig sum identity using a closed-form geometric-series derivation.
    # Let S = sum_{k=1}^{35} sin(5k°).
    # A standard sum formula gives S = sin(35*5/2°) * sin(36*5/2°) / sin(5/2°)
    # = sin(87.5°) * sin(90°) / sin(2.5°) = cos(2.5°) / sin(2.5°) = tan(87.5°).
    # We verify the algebraic simplification symbolically.
    a = Symbol('a', real=True)
    expr = sin(35*a/2) * sin(36*a/2) / sin(a/2)
    target = tan(Rational(175, 2) * pi / 180)
    # Use exact transformation at a = 5 degrees (pi/36 radians)
    val = simplify(trigsimp(expr.subs(a, pi/36) - target))
    return val == 0, f