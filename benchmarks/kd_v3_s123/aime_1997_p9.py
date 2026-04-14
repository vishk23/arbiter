from __future__ import annotations

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def _sympy_exact_proof():
    a = sp.Symbol('a', positive=True, real=True)

    # Since 2 < a^2 < 3, we have floor(a^2) = 2, so
    #   <a^2> = a^2 - 2.
    # Also a > 0 and 1/a > 0. From <1/a> = <a^2>, the only compatible
    # interpretation here is
    #   1/a = a^2 - 2,
    # giving the cubic a^3 - 2a - 1 = 0.
    eq = sp.expand(a**3 - 2*a - 1)

    # The positive root is the golden ratio phi.
    phi = (1 + sp.sqrt(5)) / 2
    assert sp.simplify(phi**2 - phi - 1) == 0
    assert sp.simplify(phi**3 - 2*phi - 1) == 0

    # Evaluate the target exactly.
    expr = sp.simplify(phi**12 - 144/phi)
    expr = sp.nsimplify(expr)
    assert expr == 233
    return {"value": expr, "cubic": eq}


def main():
    return _sympy_exact_proof()


RESULT = main()