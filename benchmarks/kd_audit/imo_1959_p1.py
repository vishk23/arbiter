from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And

from sympy import Symbol, gcd


def _proof_gcd_is_one() -> Any:
    """Verified kdrag proof that gcd(21n+4, 14n+3)=1 for all n >= 0."""
    n = Int("n")
    d = Int("d")
    # If d divides both numbers, then d divides their difference 7n+1,
    # and then d divides 1, hence d = 1 for positive d.
    return kd.prove(
        ForAll(
            [n, d],
            Implies(
                And(n >= 0, d > 0, (21 * n + 4) % d == 0, (14 * n + 3) % d == 0),
                d == 1,
            ),
        )
    )


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Verified proof check (kdrag / Z3 certificate)
    try:
        pf = _proof_gcd_is_one()
        checks.append(
            {
                "name": "gcd_divisibility_implies_unit_divisor",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof obtained: {pf}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "gcd_divisibility_implies_unit_divisor",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Symbolic sanity: SymPy gcd on the polynomial expressions is 1
    try:
        n = Symbol("n", integer=True)
        g = gcd(21 * n + 4, 14 * n + 3)
        passed = (g == 1)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "symbolic_gcd_check",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"sympy gcd(21*n+4, 14*n+3) = {g}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "symbolic_gcd_check",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"sympy gcd computation failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete natural number
    try:
        n0 = 5
        num = 21 * n0 + 4
        den = 14 * n0 + 3
        import math

        passed = math.gcd(num, den) == 1
        if not passed:
            proved = False
        checks.append(
            {
                "name": "numerical_sanity_at_n_5",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"gcd({num}, {den}) = {math.gcd(num, den)}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_at_n_5",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)