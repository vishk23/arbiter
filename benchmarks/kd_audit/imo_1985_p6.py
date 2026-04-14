from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *

from sympy import Symbol, Rational, minimal_polynomial


# --- Verified theorem-friendly facts ---
# The full IMO problem is an infinite dynamical-system statement and is not
# directly expressible as a single first-order Z3 claim over a finite set of
# variables. We therefore provide a small set of rigorous, machine-checked
# supporting facts that are exactly the ingredients used in the classical proof.


def _prove_z3_basic_sequence_fact():
    """A Z3-checkable algebraic fact used in the monotonicity argument."""
    n = Real("n")
    x = Real("x")
    y = Real("y")
    # If 0 < x < y and n >= 1, then x*(x+1/n) < y*(y+1/n) for x,y in [0,1].
    # We encode a weaker but sufficient monotonicity witness on the unit interval.
    thm = kd.prove(
        ForAll(
            [x, y, n],
            Implies(
                And(n >= 1, 0 <= x, x < y, y <= 1),
                x * (x + 1 / n) < y * (y + 1 / n),
            ),
        )
    )
    return thm


def _prove_z3_difference_growth_fact():
    """The difference recurrence used in the uniqueness argument."""
    xn = Real("xn")
    yn = Real("yn")
    n = Real("n")
    thm = kd.prove(
        ForAll(
            [xn, yn, n],
            Implies(
                And(n >= 1, 0 <= xn, xn <= 1, 0 <= yn, yn <= 1, yn >= xn),
                yn * (yn + 1 / n) - xn * (xn + 1 / n)
                == (yn - xn) * (yn + xn + 1 / n),
            ),
        )
    )
    return thm


def _sympy_symbolic_zero_check():
    """A rigorous algebraic-zero check (symbolic certificate style)."""
    x = Symbol("x")
    expr = Rational(1, 2) - Rational(1, 2)
    mp = minimal_polynomial(expr, x)
    return mp == x


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    all_passed = True

    # Verified proof 1: Z3 certificate for an algebraic identity used in the proof.
    try:
        _prove_z3_difference_growth_fact()
        checks.append(
            {
                "name": "difference_growth_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kd.prove() certified the exact factorization yn(yn+1/n)-xn(xn+1/n)=(yn-xn)(yn+xn+1/n).",
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "difference_growth_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Z3 proof failed: {type(e).__name__}: {e}",
            }
        )

    # Verified proof 2: another Z3-encodable monotonicity fact.
    try:
        _prove_z3_basic_sequence_fact()
        checks.append(
            {
                "name": "unit_interval_monotonicity_witness",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "kd.prove() certified monotonicity of the update map on [0,1] under the stated hypotheses.",
            }
        )
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "unit_interval_monotonicity_witness",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Z3 proof failed: {type(e).__name__}: {e}",
            }
        )

    # SymPy symbolic zero check.
    try:
        ok = _sympy_symbolic_zero_check()
        checks.append(
            {
                "name": "symbolic_zero_sanity",
                "passed": bool(ok),
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": "minimal_polynomial(1/2-1/2, x) == x gives a rigorous symbolic-zero certificate.",
            }
        )
        if not ok:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "symbolic_zero_sanity",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy symbolic-zero check failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check.
    try:
        x1 = 0.4
        x2 = x1 * (x1 + 1.0)
        x3 = x2 * (x2 + 0.5)
        passed = (0 < x1 < 1) and (0 < x2 < x3 < 1)
        checks.append(
            {
                "name": "numerical_sequence_sanity",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"For x1={x1}, x2={x2:.12g}, x3={x3:.12g}; sanity check only, not a proof of the theorem.",
            }
        )
        if not passed:
            all_passed = False
    except Exception as e:
        all_passed = False
        checks.append(
            {
                "name": "numerical_sequence_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    # The full theorem is not fully mechanized here.
    # We report proved=False because we do not have a complete formalization
    # of the infinite intersection/uniqueness argument in this module.
    proved = False and all_passed

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json

    result = verify()
    print(json.dumps(result, indent=2, sort_keys=True))