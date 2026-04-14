from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *

from sympy import Integer


def _proof_check_name(name: str, passed: bool, backend: str, proof_type: str, details: str) -> Dict[str, Any]:
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

    # Verified proof: the two claimed solutions satisfy the divisibility condition.
    p, q, r = Ints("p q r")
    solutions = [
        (2, 4, 8),
        (3, 5, 15),
    ]
    for idx, (pp, qq, rr) in enumerate(solutions, start=1):
        name = f"solution_{idx}_satisfies_divisibility"
        try:
            thm = kd.prove(
                (pp - 1) * (qq - 1) * (rr - 1) != 0
            )
            # If we got a proof of nonzero denominator-like factor, also verify divisibility directly by computation.
            lhs = (pp * qq * rr - 1) % ((pp - 1) * (qq - 1) * (rr - 1))
            passed = (lhs == 0)
            checks.append(
                _proof_check_name(
                    name,
                    passed,
                    "kdrag",
                    "certificate",
                    f"Computed remainder {(pp * qq * rr - 1)} mod {((pp - 1) * (qq - 1) * (rr - 1))} = {lhs}; kd.prove returned {type(thm).__name__}.",
                )
            )
            proved = proved and passed
        except Exception as e:
            checks.append(
                _proof_check_name(
                    name,
                    False,
                    "kdrag",
                    "certificate",
                    f"Verification backend error: {e}",
                )
            )
            proved = False

    # Numerical sanity check at a concrete value unrelated to the theorem statement structure.
    # Confirms the divisibility expression for the claimed solutions exactly.
    num_name = "numerical_sanity_check_claimed_solutions"
    try:
        vals = [
            ((2, 4, 8), Integer((2 * 4 * 8 - 1) // ((2 - 1) * (4 - 1) * (8 - 1)))),
            ((3, 5, 15), Integer((3 * 5 * 15 - 1) // ((3 - 1) * (5 - 1) * (15 - 1)))),
        ]
        passed = (vals[0][1] == 21) and (vals[1][1] == 28)
        checks.append(
            _proof_check_name(
                num_name,
                passed,
                "numerical",
                "numerical",
                f"Computed quotients are {vals[0][1]} and {vals[1][1]} for the two claimed solutions.",
            )
        )
        proved = proved and passed
    except Exception as e:
        checks.append(
            _proof_check_name(
                num_name,
                False,
                "numerical",
                "numerical",
                f"Numerical sanity check failed: {e}",
            )
        )
        proved = False

    # Partial verified bound from the hint: if p >= 5 then (p-1)(q-1)(r-1) > pqr-1 is not encoded fully,
    # so we state this part as unproved in the module's overall verdict.
    checks.append(
        _proof_check_name(
            "full_classification_not_encoded",
            False,
            "kdrag",
            "certificate",
            "The complete exclusion argument from the contest proof is not fully encoded in Z3 here; only the claimed solutions are checked exactly.",
        )
    )
    proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)