import math
from typing import Dict, List

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And, Or, Not, IntVal

import sympy as sp


def _integer_count_abs_bound() -> int:
    return len([k for k in range(-100, 101) if abs(k) < 3 * math.pi])


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Numerical sanity check: 3*pi is between 9 and 10.
    lower_ok = 9 < 3 * math.pi
    upper_ok = 3 * math.pi < 10
    checks.append({
        "name": "pi_bounds",
        "passed": lower_ok and upper_ok,
        "backend": "python",
        "proof_type": "computation",
        "details": f"9 < 3*pi < 10 is {lower_ok and upper_ok}",
    })
    proved = proved and lower_ok and upper_ok

    # Exact enumeration of integers satisfying |x| < 3*pi.
    count = _integer_count_abs_bound()
    checks.append({
        "name": "exact_enumeration",
        "passed": count == 19,
        "backend": "python",
        "proof_type": "computation",
        "details": f"Count is {count}",
    })
    proved = proved and (count == 19)

    # Formalized interval characterization: since 9 < 3*pi < 10,
    # the integers with |x| < 3*pi are exactly -9,...,9.
    x = Int("x")
    try:
        # This is a valid integer fact because every integer in [-9,9] satisfies |x| < 3*pi.
        thm = kd.prove(
            ForAll([x], Implies(And(x >= -9, x <= 9), x * x < (3 * math.pi) * (3 * math.pi)))
        )
        checks.append({
            "name": "integer_interval_soundness",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "theorem",
            "details": str(thm),
        })
    except Exception as e:
        checks.append({
            "name": "integer_interval_soundness",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "theorem",
            "details": f"kdrag proof failed: {e}",
        })
        proved = False

    return {"proved": proved, "checks": checks}