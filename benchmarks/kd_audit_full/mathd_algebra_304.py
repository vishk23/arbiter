from __future__ import annotations

import kdrag as kd
from kdrag.smt import Int


def verify() -> dict:
    checks = []
    proved = True

    # Verified proof: arithmetic expansion of 91^2.
    try:
        n = Int("n")
        thm = kd.prove((91 * 91) == 8281)
        checks.append(
            {
                "name": "91_squared_equals_8281_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove certified the closed arithmetic statement: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "91_squared_equals_8281_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof attempt failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check
    try:
        value = 91 ** 2
        passed = value == 8281
        checks.append(
            {
                "name": "91_squared_numerical_sanity",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed 91**2 = {value}; expected 8281.",
            }
        )
        proved = proved and passed
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "91_squared_numerical_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)