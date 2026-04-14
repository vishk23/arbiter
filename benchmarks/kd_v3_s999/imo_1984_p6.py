from typing import Dict

import kdrag as kd
from kdrag.smt import *


def _no_counterexample_a_gt_1_check() -> Dict:
    """Encode the problem and ask Z3 for a counterexample with a > 1.

    Let
        u = (b-a)/2 > 0,
        v = (d-c)/2 > 0.
    From ad = bc and a+d = 2^k, b+c = 2^m, one derives
        (b-a)(d-c) = (a+d)(b+c) - 2(ad+bc) - 2(a c + b d)
    is not the right route for direct encoding.

    Instead, use the standard parameterization coming from
        ad = bc  =>  a/c = b/d,
    together with the strict ordering and oddness. For odd integers,
    write
        b = a + 2u,
        c = d - 2v.
    Then ad = bc implies
        a d = (a + 2u)(d - 2v)
        0 = 2u d - 2av - 4uv
        ad = av + 2uv ?
    Rather than over-encoding the derivation, we directly search for a
    counterexample satisfying the original constraints and a > 1.

    If the problem statement is correct, Z3 should report UNSAT.
    """
    a, b, c, d, k, m = Ints("a b c d k m")
    s = Solver()

    # Basic hypotheses
    s.add(a > 0, a < b, b < c, c < d)
    s.add(a % 2 == 1, b % 2 == 1, c % 2 == 1, d % 2 == 1)
    s.add(a * d == b * c)
    s.add(a + d == 2 ** k)
    s.add(b + c == 2 ** m)

    # Counterexample target
    s.add(a > 1)

    # Ask Z3 if such a counterexample exists.
    result = s.check()
    return {
        "counterexample_exists": result == sat,
        "model": str(s.model()) if result == sat else None,
        "check": str(result),
    }


def _small_search_sanity_check() -> Dict:
    """Brute-force sanity check for small values.

    This is not a proof, but it helps verify that the expected
    conclusion a = 1 matches small instances.
    """
    sols = []
    for a in range(1, 51, 2):
        for b in range(a + 2, 51, 2):
            for c in range(b + 2, 51, 2):
                for d in range(c + 2, 51, 2):
                    if a * d != b * c:
                        continue
                    s1 = a + d
                    s2 = b + c
                    if s1 > 0 and s2 > 0 and (s1 & (s1 - 1)) == 0 and (s2 & (s2 - 1)) == 0:
                        sols.append((a, b, c, d, s1, s2))
    return {"solutions": sols, "found": len(sols) > 0}