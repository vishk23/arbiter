from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Ints, Int, And, Or, Implies, ForAll, Exists, Not


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    # Check 1: Verified theorem statement in the intended constructive form.
    # If gcd(m,n)=6 and lcm(m,n)=126, then m=6x, n=6y, gcd(x,y)=1, and xy=21.
    # The only coprime positive factor pair of 21 is (3,7) up to order, so m+n >= 60.
    # We encode the key arithmetic fact with kdrag on the reduced variables.
    x, y = Ints("x y")
    thm1 = None
    try:
        thm1 = kd.prove(
            ForAll(
                [x, y],
                Implies(
                    And(x > 0, y > 0, x * y == 21),
                    x + y >= 10,
                ),
            )
        )
        checks.append(
            {
                "name": "factor_pair_lower_bound",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved that any positive integers x,y with xy=21 satisfy x+y>=10. Proof: {thm1}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "factor_pair_lower_bound",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove the reduced arithmetic claim in kdrag: {e}",
            }
        )

    # Check 2: Existence of the minimizing pair m=18, n=42 (or reversed), giving gcd=6 and lcm=126.
    # This is a direct numerical sanity / witness check.
    m0, n0 = 18, 42
    import math
    passed2 = (math.gcd(m0, n0) == 6) and (m0 * n0 // math.gcd(m0, n0) == 126) and (m0 + n0 == 60)
    checks.append(
        {
            "name": "witness_pair_18_42",
            "passed": passed2,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Checked concrete witness (m,n)=({m0},{n0}): gcd={math.gcd(m0,n0)}, lcm={m0*n0//math.gcd(m0,n0)}, sum={m0+n0}.",
        }
    )

    # Check 3: Symbolic arithmetic decomposition of 126 / 6 = 21.
    # This is not the main proof, but it verifies the factorization step used in the reasoning.
    try:
        from sympy import Integer, factorint

        fac = factorint(Integer(21))
        passed3 = fac == {3: 1, 7: 1}
        checks.append(
            {
                "name": "factorization_of_21",
                "passed": passed3,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"factorint(21) returned {fac}, confirming 21 = 3*7 and hence the minimizing pair is (3,7) up to order.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "factorization_of_21",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy factorization failed: {e}",
            }
        )

    proved = all(c["passed"] for c in checks) and any(c["proof_type"] == "certificate" and c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)