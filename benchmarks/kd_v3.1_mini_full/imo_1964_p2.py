from __future__ import annotations

from typing import Dict, Any

import kdrag as kd
from kdrag.smt import Real, ForAll


def _proof_check_ineq() -> Dict[str, Any]:
    """Prove a^2(b+c-a)+b^2(c+a-b)+c^2(a+b-c) <= 3abc for triangle sides.

    Use the standard substitution
        a = y+z, b = z+x, c = x+y
    with x, y, z >= 0.

    Then
        b+c-a = 2x,
        c+a-b = 2y,
        a+b-c = 2z,
    and the inequality becomes
        2x(y+z)^2 + 2y(z+x)^2 + 2z(x+y)^2 <= 3(x+y)(y+z)(z+x),
    which simplifies to the classical factorization
        3abc - [a^2(b+c-a)+b^2(c+a-b)+c^2(a+b-c)]
        = (x+y+z)(xy+yz+zx-? )
    However, rather than rely on a nontrivial factorization inside Z3, we
    verify the exact polynomial identity after substitution directly by
    symbolic expansion.
    """
    x, y, z = Real("x"), Real("y"), Real("z")
    a, b, c = y + z, z + x, x + y

    lhs = a * a * (b + c - a) + b * b * (c + a - b) + c * c * (a + b - c)
    rhs = 3 * a * b * c

    # After substitution, the difference is a polynomial identity.
    goal = ForAll([x, y, z], rhs - lhs == 2 * (x + y + z) * (x * y + y * z + z * x))
    kd.prove(goal)
    return {"name": "algebraic_substitution_identity", "result": True}


def check() -> Dict[str, Any]:
    return _proof_check_ineq()