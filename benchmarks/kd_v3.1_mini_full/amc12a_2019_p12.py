from __future__ import annotations

import math
from typing import Any, Dict, List

import sympy as sp

try:
    import kdrag as kd
    from kdrag.smt import *
except Exception:  # pragma: no cover
    kd = None


def _sympy_symbolic_proof() -> Dict[str, Any]:
    a = sp.symbols('a', nonzero=True)
    sol = sp.solve(sp.Eq(a + 4 / a, 6), a)
    vals = [sp.simplify((s - 4 / s) ** 2) for s in sol]
    passed = all(v == 20 for v in vals) and set(sol) == {2, 4}
    return {
        "name": "sympy algebraic derivation",
        "passed": bool(passed),
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Solved a + 4/a = 6 with solutions {sol}; computed (a - 4/a)^2 = {vals}.",
    }


def _kdrag_proof() -> Dict[str, Any]:
    if kd is None:
        return {
            "name": "kdrag certificate for derived polynomial equation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag unavailable in this environment.",
        }

    try:
        a = Real('a')
        # From a + 4/a = 6, derive a^2 - 6a + 4 = 0 by clearing denominators.
        thm = kd.prove(ForAll([a], Implies(And(a != 0, a + 4 / a == 6), a * a - 6 * a + 4 == 0)))
        return {
            "name": "kdrag certificate for derived polynomial equation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified implication with proof object: {thm}.",
        }
    except Exception as e:
        return {
            "name": "kdrag certificate for derived polynomial equation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        }


def _numerical_check() -> Dict[str, Any]:
    # Sanity-check the two roots a=2,4 correspond to the target value 20.
    vals = []
    for a in (2.0, 4.0):
        x = 2 ** a
        y = 2 ** (4 / a)
        vals.append((math.log(x / y, 2)) ** 2)
    passed = all(abs(v - 20.0) < 1e-12 for v in vals)
    return {
        "name": "numerical sanity check at concrete solutions",
        "passed": passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Evaluated at a=2 and a=4, obtaining {vals}.",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    checks.append(_sympy_symbolic_proof())
    checks.append(_kdrag_proof())
    checks.append(_numerical_check())
    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json
    print(json.dumps(verify(), indent=2))