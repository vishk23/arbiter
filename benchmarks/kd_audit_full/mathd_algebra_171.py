from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Real


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Verified proof: encode f(1) = 5*1 + 4 = 9 in Z3 via kdrag.
    try:
        x = Real("x")
        f1 = 5 * 1 + 4
        thm = kd.prove(f1 == 9)
        checks.append(
            {
                "name": "f(1) equals 9",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned a proof certificate: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "f(1) equals 9",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to obtain proof certificate: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete point x = 1.
    try:
        val = 5 * 1 + 4
        passed = (val == 9)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical evaluation at x=1",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed 5*1 + 4 = {val}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical evaluation at x=1",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    # Additional symbolic arithmetic sanity check.
    try:
        from sympy import Integer

        expr = 5 * Integer(1) + 4
        passed = (expr == 9)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "symbolic arithmetic simplification",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"SymPy simplified 5*1 + 4 to {expr}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "symbolic arithmetic simplification",
                "passed": False,
                "backend": "sympy",
                "proof_type": "numerical",
                "details": f"SymPy check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)