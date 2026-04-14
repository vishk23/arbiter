from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, And, Implies, ForAll


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Verified proof: encode the AMC relation and prove the unique difference.
    # Let the smaller number be a, so the larger number is 10a.
    # Given 10a + a = 17402, derive a = 1582 and difference = 9a = 14238.
    a = Int("a")
    diff = Int("diff")

    try:
        thm = kd.prove(
            ForAll(
                [a, diff],
                Implies(
                    And(11 * a == 17402, diff == 9 * a),
                    diff == 14238,
                ),
            )
        )
        checks.append(
            {
                "name": "symbolic_derivation_of_difference",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "symbolic_derivation_of_difference",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete solution a = 1582.
    try:
        a_val = 1582
        larger = 10 * a_val
        smaller = a_val
        total = larger + smaller
        diff_val = larger - smaller
        passed = (total == 17402) and (diff_val == 14238) and (larger % 10 == 0)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"a={a_val}, larger={larger}, smaller={smaller}, total={total}, difference={diff_val}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)