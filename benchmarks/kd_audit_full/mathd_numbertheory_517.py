from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Prove the modular residue directly by arithmetic.
    try:
        val = 121 * 122 * 123
        residue = val % 4
        thm = kd.prove(residue == 2)
        checks.append(
            {
                "name": "mod4_residue_121_122_123",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified that 121*122*123 % 4 == 2. Proof: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "mod4_residue_121_122_123",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check
    try:
        val = 121 * 122 * 123
        residue = val % 4
        passed = (residue == 2)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"121*122*123 = {val}, and {val} % 4 = {residue}.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)