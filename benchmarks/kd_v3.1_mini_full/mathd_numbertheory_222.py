from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import Int, IntVal, ForAll, Implies, And


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []

    # Verified proof: show the arithmetic identity needed for the problem.
    # From gcd(a,b) * lcm(a,b) = a*b, with gcd = 8, lcm = 3720, and a = 120,
    # the other number is b = 8*3720/120 = 248.
    a = Int("a")
    b = Int("b")

    # Encode the concrete arithmetic claim as a theorem in Z3.
    thm = ForAll(
        [a, b],
        Implies(
            And(a == 120, b == 248),
            a * b == IntVal(3720) * IntVal(8),
        ),
    )

    try:
        proof = kd.prove(thm)
        checks.append(
            {
                "name": "product_identity_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {proof}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "product_identity_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: compute the implied other number.
    lcm_val = 3720
    gcd_val = 8
    given = 120
    other = (lcm_val * gcd_val) // given
    checks.append(
        {
            "name": "numerical_other_number",
            "passed": other == 248,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"(3720 * 8) // 120 = {other}",
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)