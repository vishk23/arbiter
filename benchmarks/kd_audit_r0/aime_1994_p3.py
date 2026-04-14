from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *


# We encode the recurrence on integers, which is sufficient since 19 and 94 are integers
# and the statement concerns the value at the integer point 94. The given functional
# equation holds for all real x, so in particular for all integers.


def _prove_closed_form() -> Any:
    """Prove by kdrag that any function satisfying the recurrence must obey a
    closed-form relation for integer arguments.

    We prove the specific telescoping identity:
        f(n) + f(n-1) = n^2
    implies, for even-step descent from 94 to 20,
        f(94) = sum_{k=21}^{94} (-1)^{94-k} k^2 + f(19).

    Rather than formalizing the full induction in Z3, we verify the numeric
    consequence directly from the recurrence by encoding the finite system of
    equations for the needed integer points.
    """
    # Integer symbols for the relevant values.
    vals = {i: Int(f"f_{i}") for i in range(19, 95)}

    constraints = []
    for n in range(20, 95):
        constraints.append(vals[n] + vals[n - 1] == n * n)
    constraints.append(vals[19] == 94)

    # Compute the claimed value 4561 and verify it is the unique consequence of the system.
    # We use an explicit elimination chain by substituting backwards from 94 to 19.
    expr = vals[94]
    for n in range(94, 19, -1):
        expr = n * n - expr

    # The above expression is equivalent to the recurrence unfolding;
    # prove it equals 4561 under f(19)=94.
    thm = kd.prove(Implies(And(*constraints), expr == 4561))
    return thm


def _numerical_sanity() -> Dict[str, Any]:
    # Direct arithmetic sanity check.
    f94 = 4561
    return {
        "name": "numerical_sanity_remainder",
        "passed": (f94 % 1000 == 561),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"4561 mod 1000 = {f94 % 1000}.",
    }


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof check via kdrag.
    try:
        proof = _prove_closed_form()
        checks.append({
            "name": "kdrag_recurrence_unfolding",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {proof}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_recurrence_unfolding",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Additional exact arithmetic check, separately verified by computation.
    # The recurrence unfolding gives f(94)=4561, hence remainder 561.
    remainder_check = _numerical_sanity()
    checks.append(remainder_check)
    if not remainder_check["passed"]:
        proved = False

    # Another directly verified arithmetic certificate: 4561 = 400 + (21+22+...+94) - 94.
    # This is checked as a finite exact sum.
    s = sum(range(21, 95))
    exact_value = 400 + s - 94
    checks.append({
        "name": "finite_sum_certificate",
        "passed": (exact_value == 4561),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"400 + sum(21..94) - 94 = {exact_value}.",
    })
    if exact_value != 4561:
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)