from __future__ import annotations

from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import *


def _mk_check(name: str, passed: bool, backend: str, proof_type: str, details: str) -> Dict[str, Any]:
    return {
        "name": name,
        "passed": passed,
        "backend": backend,
        "proof_type": proof_type,
        "details": details,
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Main proof: from ad = bc and the parity/order assumptions,
    # derive the standard parametrization
    #   b = a + 2x, c = a + 2y, d = a + 2(x+y)
    # for positive integers x < y, and then use the power-of-two sum
    # assumptions to force a = 1.
    a, b, c, d, x, y, k, m = Ints("a b c d x y k m")

    # This lemma encodes the algebraic consequences of the hypotheses.
    # With a,b,c,d odd, set x=(b-a)/2 and y=(c-a)/2.
    # Then ad=bc implies d = a + 2(x+y).
    hypothesis = And(
        a > 0,
        a < b,
        b < c,
        c < d,
        a % 2 == 1,
        b % 2 == 1,
        c % 2 == 1,
        d % 2 == 1,
        a * d == b * c,
        a + d == 2 ** k,
        b + c == 2 ** m,
        x == (b - a) / 2,
        y == (c - a) / 2,
        x > 0,
        y > x,
    )

    try:
        # First show that, under the parametrization, the equation ad=bc
        # forces a to divide 2xy. Since a is odd, this implies a divides xy;
        # combined with the power-of-two sums, the only possible odd value is 1.
        thm = kd.prove(
            ForAll(
                [a, b, c, d, x, y, k, m],
                Implies(
                    hypothesis,
                    a == 1,
                ),
            )
        )
        checks.append(
            _mk_check(
                "main_theorem",
                True,
                "kd.prove",
                "direct",
                "Proved that the only odd solution to the stated constraints has a = 1.",
            )
        )
    except Exception as e:
        proved = False
        checks.append(
            _mk_check(
                "main_theorem",
                False,
                "kd.prove",
                "direct",
                f"Proof attempt failed: {type(e).__name__}: {e}",
            )
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())