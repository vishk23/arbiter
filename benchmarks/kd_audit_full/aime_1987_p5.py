from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Ints, Int, ForAll, Implies, And


def _kdrag_proof_main() -> Any:
    """Prove the core theorem in Z3: if y^2 + 3x^2y^2 = 30x^2 + 517 then 3x^2y^2 = 588."""
    x, y = Ints("x y")
    premise = y * y + 3 * x * x * y * y == 30 * x * x + 517
    conclusion = 3 * x * x * y * y == 588
    return kd.prove(ForAll([x, y], Implies(premise, conclusion)))


def _kdrag_proof_factor_form() -> Any:
    """Prove the factorization identity used in the human solution."""
    x, y = Ints("x y")
    lhs = y * y + 3 * x * x * y * y - 30 * x * x
    rhs = (3 * x * x + 1) * (y * y - 10) - 507
    return kd.prove(ForAll([x, y], lhs == rhs))


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof 1: main theorem
    try:
        pf = _kdrag_proof_main()
        checks.append({
            "name": "main_theorem_3x2y2_equals_588",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {pf}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "main_theorem_3x2y2_equals_588",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Verified proof 2: factorization identity
    try:
        pf = _kdrag_proof_factor_form()
        checks.append({
            "name": "factorization_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {pf}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "factorization_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check on the claimed solution x=2, y=7
    try:
        x_val, y_val = 2, 7
        lhs = y_val * y_val + 3 * x_val * x_val * y_val * y_val
        rhs = 30 * x_val * x_val + 517
        target = 3 * x_val * x_val * y_val * y_val
        ok = (lhs == rhs) and (target == 588)
        checks.append({
            "name": "numerical_sanity_x2_y7",
            "passed": ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For x=2, y=7: lhs={lhs}, rhs={rhs}, 3x^2y^2={target}.",
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_x2_y7",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)