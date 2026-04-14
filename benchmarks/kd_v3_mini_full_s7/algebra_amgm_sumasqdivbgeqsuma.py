from fractions import Fraction
import math

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Check 1: Verified proof by reducing the target inequality to a sum of AM-GM instances.
    # For positive reals x,y, (x^2 / y) + y >= 2x, because
    # (x^2 / y) + y - 2x = (x - y)^2 / y >= 0.
    # Summing the four cyclic instances gives
    #   (a^2/b + b^2/c + c^2/d + d^2/a) + (a+b+c+d) >= 2(a+b+c+d),
    # hence the target inequality.
    a, b, c, d = Reals("a b c d")
    target = ForAll(
        [a, b, c, d],
        Implies(
            And(a > 0, b > 0, c > 0, d > 0),
            a * a / b + b * b / c + c * c / d + d * d / a >= a + b + c + d,
        ),
    )

    try:
        # This is a pure arithmetic inequality over positive reals, suitable for Z3.
        # We ask kdrag to prove the quantified statement directly.
        pf = kd.prove(target)
        checks.append(
            {
                "name": "AM-GM cyclic inequality proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {pf}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "AM-GM cyclic inequality proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag failed to prove the quantified inequality: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Symbolic decomposition of each AM-GM term.
    # We verify numerically-symbolically that
    #   x^2/y + y - 2x = (x-y)^2/y
    # at sample symbolic-positive assignments by exact arithmetic.
    # This is a sanity check, not the main proof.
    try:
        vals = [(2, 3), (5, 7), (11, 13)]
        ok = True
        for x0, y0 in vals:
            lhs = Fraction(x0 * x0, y0) + Fraction(y0, 1) - 2 * x0
            rhs = Fraction((x0 - y0) * (x0 - y0), y0)
            if lhs != rhs or lhs < 0:
                ok = False
                break
        checks.append(
            {
                "name": "AM-GM identity sanity",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Checked exact rational instances of x^2/y + y - 2x = (x-y)^2/y >= 0.",
            }
        )
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "AM-GM identity sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Concrete numerical verification of the original inequality.
    try:
        a0, b0, c0, d0 = 2.0, 3.0, 5.0, 7.0
        lhs = a0 * a0 / b0 + b0 * b0 / c0 + c0 * c0 / d0 + d0 * d0 / a0
        rhs = a0 + b0 + c0 + d0
        ok = lhs >= rhs - 1e-12
        checks.append(
            {
                "name": "Concrete instance check",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At (a,b,c,d)=({a0},{b0},{c0},{d0}), lhs={lhs}, rhs={rhs}.",
            }
        )
        proved = proved and ok
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "Concrete instance check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Concrete evaluation failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)