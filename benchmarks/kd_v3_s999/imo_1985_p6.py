from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


def _check_basic_recurrence_consistency() -> Dict[str, object]:
    name = "basic_recurrence_consistency"
    try:
        n = Int('n')
        x = Real('x')
        xp = Real('xp')
        # If x_{n+1} = x_n(x_n + 1/n) and 0 < x_n < 1, then x_{n+1} is well-defined.
        thm = kd.prove(
            ForAll([n, x],
                  Implies(And(n >= 1, x > 0, x < 1),
                          x * (x + 1 / n) > 0))
        )
        return {
            "name": name,
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified with kd.prove: {thm}",
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        }


def _check_numerical_sanity() -> Dict[str, object]:
    name = "numerical_sanity_sample_orbit"
    try:
        x1 = 0.2
        xs = [x1]
        ok = True
        details_parts = []
        for n in range(1, 8):
            xn = xs[-1]
            xnext = xn * (xn + 1.0 / n)
            details_parts.append(f"n={n}: x_n={xn:.12f}, x_{n+1}={xnext:.12f}")
            if not (0 < xn < xnext < 1):
                ok = False
                break
            xs.append(xnext)
        return {
            "name": name,
            "passed": ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(details_parts),
        }
    except Exception as e:
        return {
            "name": name,
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical check failed: {type(e).__name__}: {e}",
        }


def run_checks() -> List[Dict[str, object]]:
    return [
        _check_basic_recurrence_consistency(),
        _check_numerical_sanity(),
    ]