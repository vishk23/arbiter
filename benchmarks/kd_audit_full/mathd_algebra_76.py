from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, If, And


def f(n):
    """Piecewise integer function from the problem statement."""
    return If(n % 2 != 0, n * n, n * n - 4 * n - 1)


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: compute the nested value exactly in Z3/Knuckledragger.
    try:
        n = Int("n")
        # First prove the concrete inner evaluations used in the chain.
        c1 = kd.prove(f(4) == -1)
        c2 = kd.prove(f(-1) == 1)
        c3 = kd.prove(f(1) == 1)
        # Then prove the full nested expression.
        thm = kd.prove(f(f(f(f(f(4))))) == 1)
        checks.append({
            "name": "concrete_chain_evaluation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by Knuckledragger proofs: {c1}, {c2}, {c3}, and final theorem {thm}.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "concrete_chain_evaluation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Knuckledragger proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at the concrete value 4.
    try:
        def f_py(n: int) -> int:
            return n * n if (n % 2 != 0) else (n * n - 4 * n - 1)

        v1 = f_py(4)
        v2 = f_py(v1)
        v3 = f_py(v2)
        v4 = f_py(v3)
        v5 = f_py(v4)
        passed = (v1, v2, v3, v4, v5) == (-1, 1, 1, 1, 1)
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_sanity_chain",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed chain: f(4)={v1}, f(f(4))={v2}, f^3(4)={v3}, f^4(4)={v4}, f^5(4)={v5}.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_chain",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)