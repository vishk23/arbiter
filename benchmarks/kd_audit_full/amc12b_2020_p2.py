from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Real, ForAll, Implies

from sympy import Integer


# Verified algebraic proof using kdrag/Z3.
# We prove the expression is identically 1 for all real x, y with x != y (and x + y != 0),
# then instantiate it at x=100, y=7 and x=70, y=11 via a concrete numerical check.


def _prove_symbolic_identity():
    x = Real("x")
    y = Real("y")

    expr = ((x**2 - y**2) / ((x - y) * (x + y))) * (((x - y) * (x + y)) / (x**2 - y**2))
    thm = kd.prove(ForAll([x, y], Implies((x**2 - y**2) != 0, expr == 1)))
    return thm


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: certified symbolic proof of the algebraic cancellation identity.
    try:
        proof = _prove_symbolic_identity()
        checks.append({
            "name": "symbolic_cancellation_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned Proof: {proof}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "symbolic_cancellation_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: exact arithmetic evaluation of the given AMC expression.
    try:
        val = ((Integer(100)**2 - Integer(7)**2) / (Integer(70)**2 - Integer(11)**2)) * \
              (((Integer(70) - Integer(11)) * (Integer(70) + Integer(11))) / ((Integer(100) - Integer(7)) * (Integer(100) + Integer(7))))
        passed = (val == 1)
        if not passed:
            proved = False
        checks.append({
            "name": "exact_evaluation_at_problem_values",
            "passed": bool(passed),
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"Exact evaluation gives {val}; expected 1.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "exact_evaluation_at_problem_values",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Evaluation failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)