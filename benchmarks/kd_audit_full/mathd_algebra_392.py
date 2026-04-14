from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, And, Implies, ForAll


def _prove_main_theorem():
    """Formal proof of the core algebraic claim using kdrag/Z3."""
    n = Int("n")

    # If three consecutive positive even numbers are n-2, n, n+2 and their
    # squares sum to 12296, then n must be 64.
    premise = And(n > 0, (n - 2) % 2 == 0, n % 2 == 0, (n + 2) % 2 == 0,
                  (n - 2) * (n - 2) + n * n + (n + 2) * (n + 2) == 12296)

    concl = (n == 64)
    return kd.prove(ForAll([n], Implies(premise, concl)))


def _prove_product_claim():
    """Formal proof that the product/8 equals 32736 for n = 64."""
    n = Int("n")
    return kd.prove((62 * 64 * 66) / 8 == 32736)


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof: derive the middle number from the square-sum equation.
    try:
        pf1 = _prove_main_theorem()
        checks.append({
            "name": "derive_middle_number",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {pf1}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "derive_middle_number",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Verified proof: the final product/8 calculation.
    try:
        pf2 = _prove_product_claim()
        checks.append({
            "name": "product_divided_by_8",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {pf2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "product_divided_by_8",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at the concrete values 62, 64, 66.
    a, b, c = 62, 64, 66
    squares_sum = a * a + b * b + c * c
    product_div_8 = (a * b * c) // 8
    num_passed = (squares_sum == 12296) and (product_div_8 == 32736)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": num_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"sum of squares = {squares_sum}, product/8 = {product_div_8}",
    })
    proved = proved and num_passed

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)