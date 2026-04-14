from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


# Formal theorem: for all natural numbers n, gcd(21n+4, 14n+3) = 1.
# This implies the fraction (21n+4)/(14n+3) is irreducible.

n = Int("n")

# Since kd.smt has no gcd, we prove the Euclidean step directly:
# gcd(21n+4, 14n+3) = gcd((21n+4) - (14n+3), 14n+3)
#                  = gcd(7n+1, 14n+3)
# and then
# (14n+3) - 2*(7n+1) = 1,
# so any common divisor divides 1, hence is 1.
# We encode the arithmetic identities used in the reduction.

step1 = ForAll(
    [n],
    Implies(n >= 0, (21 * n + 4) - (14 * n + 3) == 7 * n + 1),
)

step2 = ForAll(
    [n],
    Implies(n >= 0, (14 * n + 3) - 2 * (7 * n + 1) == 1),
)

# Main theorem stated as a divisibility fact sufficient for irreducibility:
# any common divisor d of numerator and denominator must divide 1.
# This is equivalent to gcd = 1.

d = Int("d")
main_theorem = ForAll(
    [n, d],
    Implies(
        And(n >= 0, d > 0, (21 * n + 4) % d == 0, (14 * n + 3) % d == 0),
        d == 1,
    ),
)


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    try:
        p1 = kd.prove(step1)
        checks.append(
            {
                "name": "euclidean_reduction_step_1",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved arithmetic identity certificate: {p1}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "euclidean_reduction_step_1",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove reduction identity: {e}",
            }
        )

    try:
        p2 = kd.prove(step2)
        checks.append(
            {
                "name": "euclidean_reduction_step_2",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved remainder-one certificate: {p2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "euclidean_reduction_step_2",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove remainder-one identity: {e}",
            }
        )

    try:
        p3 = kd.prove(main_theorem)
        checks.append(
            {
                "name": "irreducible_fraction_main_theorem",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved irreducibility theorem certificate: {p3}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "irreducible_fraction_main_theorem",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to prove main theorem: {e}",
            }
        )

    return {"proved": proved, "checks": checks}