from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved_all = True

    # Verified proof: the remainder is 9, encoded as a modular arithmetic theorem.
    # We prove 129^34 + 96^38 ≡ 9 (mod 11), equivalently divisibility by 11.
    try:
        thm = kd.prove(
            (129**34 + 96**38 - 9) % 11 == 0
        )
        checks.append(
            {
                "name": "modular_remainder_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {thm}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "modular_remainder_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof attempt failed: {type(e).__name__}: {e}",
            }
        )

    # A second verified arithmetic certificate: 129 ≡ 96 ≡ -3 (mod 11).
    # This is a simple sanity theorem in modular arithmetic.
    try:
        x = Int("x")
        y = Int("y")
        mod_lem = kd.prove(
            ForAll([x, y], Implies(And(x == 129, y == 96), And((x + 3) % 11 == 0, (y + 3) % 11 == 0)))
        )
        checks.append(
            {
                "name": "congruence_sanity_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {mod_lem}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "congruence_sanity_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof attempt failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete values.
    try:
        value_mod = (129**34 + 96**38) % 11
        ok = value_mod == 9
        checks.append(
            {
                "name": "numerical_sanity_remainder",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"(129**34 + 96**38) % 11 = {value_mod}",
            }
        )
        proved_all = proved_all and ok
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_remainder",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical evaluation failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)