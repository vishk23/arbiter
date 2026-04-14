from __future__ import annotations

from typing import Dict, List

import math

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # We solve the Diophantine equation directly.
    # Let u = x^2 and v = y^2. Then
    #   v + 3uv = 30u + 517
    # so v(1 + 3u) = 30u + 517.
    # Rewrite as
    #   (3u + 1)(v - 10) = 527 = 17 * 31.
    # Since u, v are nonnegative integers, 3u+1 is a positive divisor of 527.
    # The only divisor compatible with v being a square is 13, giving u = 4 and v = 49,
    # hence 3x^2 y^2 = 3*u*v = 588.

    target_value = 588

    # Check 1: brute-force confirmation over all factor pairs of 527.
    # This avoids relying on a missing sympy.isqrt call.
    candidates = []
    n = 527
    for d in range(1, int(math.isqrt(n)) + 1):
        if n % d == 0:
            for dd in (d, n // d):
                if (dd - 1) % 3 == 0:
                    u = (dd - 1) // 3
                    vv = 10 + n // dd
                    r = int(math.isqrt(vv))
                    if r * r == vv:
                        candidates.append((u, vv))

    if candidates == [(4, 49)]:
        checks.append(
            {
                "name": "diophantine_factor_search",
                "passed": True,
                "backend": "python",
                "proof_type": "search",
                "details": "Unique solution in nonnegative integers is x^2 = 4 and y^2 = 49.",
            }
        )
    else:
        checks.append(
            {
                "name": "diophantine_factor_search",
                "passed": False,
                "backend": "python",
                "proof_type": "search",
                "details": f"Unexpected candidates: {candidates}",
            }
        )
        proved = False

    # Check 2: formalized arithmetic consequence using kdrag if available.
    if kd is None:
        checks.append(
            {
                "name": "kdrag_arithmetic_consequence",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "formal",
                "details": "kdrag is unavailable in this environment.",
            }
        )
        proved = False
    else:
        x = Int("x")
        y = Int("y")
        u = Int("u")
        v = Int("v")
        # Encode only the key reduction; if unprovable, fall back to the Python search above.
        try:
            kd.prove(
                ForAll(
                    [x, y],
                    Implies(
                        y * y + 3 * x * x * y * y == 30 * x * x + 517,
                        3 * x * x * y * y == target_value,
                    ),
                )
            )
            checks.append(
                {
                    "name": "kdrag_arithmetic_consequence",
                    "passed": True,
                    "backend": "kdrag",
                    "proof_type": "formal",
                    "details": "Proved directly with kdrag.",
                }
            )
        except Exception as e:
            checks.append(
                {
                    "name": "kdrag_arithmetic_consequence",
                    "passed": False,
                    "backend": "kdrag",
                    "proof_type": "formal",
                    "details": f"kdrag proof failed: {type(e).__name__}: {e}",
                }
            )
            proved = False

    return {
        "proved": proved,
        "checks": checks,
        "answer": target_value,
    }