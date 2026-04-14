from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: Core algebraic lemma encoded in Z3.
    # If y = 1/2 + sqrt(x - x^2), then y(1-y) = (1/2 - x)^2.
    x, y = Reals("x y")
    core_lemma = ForAll(
        [x, y],
        Implies(
            And(y == RealVal("1/2") + Sqrt(x - x * x), x - x * x >= 0),
            y * (1 - y) == (RealVal("1/2") - x) * (RealVal("1/2") - x),
        ),
    )
    try:
        proof1 = kd.prove(core_lemma)
        checks.append(
            {
                "name": "core_algebraic_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified by kd.prove(); proof={proof1}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "core_algebraic_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove core algebraic identity: {e}",
            }
        )

    # Check 2: Abstract periodicity step encoded as a theorem over an arbitrary function f.
    # Assume f(x+a) = 1/2 + sqrt(f(x)-f(x)^2), then f(x+2a) = f(x).
    # We use an uninterpreted function plus the defining recurrence as an axiom.
    xr, a = Reals("xr a")
    f = Function("f", RealSort(), RealSort())
    recurrence = ForAll(
        [xr],
        f(xr + a) == RealVal("1/2") + Sqrt(f(xr) - f(xr) * f(xr)),
    )
    periodic_goal = ForAll([xr], f(xr + 2 * a) == f(xr))
    try:
        # The claim is not directly Z3-encodable with the chosen uninterpreted recurrence,
        # because the square-root branch and the needed algebraic case split are not fully
        # available in pure QF_NRA without additional axioms about the codomain of f.
        # Therefore we do not fake a proof; instead we record this as a non-proof check.
        raise kd.kernel.LemmaError(
            "Direct proof of periodicity from the functional equation is not encoded as a single Z3 certificate."
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "periodicity_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": (
                    "Could not produce a direct kd.prove certificate for the full periodicity statement. "
                    "The intended mathematical argument is valid: letting y=f(x), the recurrence gives "
                    "f(x+a)=1/2+sqrt(y-y^2), hence f(x+a)(1-f(x+a))=(1/2-y)^2 and therefore "
                    "f(x+2a)=1/2+sqrt((1/2-y)^2)=f(x). However, encoding the square-root branch "
                    f"into a single Z3 certificate was not completed here. Error/remark: {e}"
                ),
            }
        )

    # Check 3: Numerical sanity check on a concrete periodic example.
    # Example function satisfying the relation: f(x) = 1/2 for all x, any a>0.
    # Then f(x+a) = 1/2 and RHS = 1/2 + sqrt(1/2 - 1/4) = 1/2 + 1/2 = 1.
    # This shows the recurrence is not satisfied by the constant 1/2 function, so instead
    # we use the constructed periodic solution f(x)=sin^2(pi*x/(2a))? But the given recurrence
    # does not hold for that either globally. So the numerical check is only a sanity check of
    # the derived algebraic identity, not of the theorem statement.
    import math

    y0 = 0.3
    lhs = (0.5 + math.sqrt(y0 - y0 * y0)) * (1 - (0.5 + math.sqrt(y0 - y0 * y0)))
    rhs = (0.5 - y0) ** 2
    passed_num = abs(lhs - rhs) < 1e-12
    checks.append(
        {
            "name": "numerical_identity_sanity",
            "passed": passed_num,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": (
                f"Checked at y={y0}: lhs={lhs}, rhs={rhs}, abs diff={abs(lhs-rhs)}. "
                "This sanity check confirms the algebraic transformation used in the proof sketch."
            ),
        }
    )
    proved = proved and passed_num

    # Overall result: since the full theorem was not encoded as a certified proof,
    # we conservatively report proved=False.
    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2))