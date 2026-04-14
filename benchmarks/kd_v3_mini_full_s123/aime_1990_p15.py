from __future__ import annotations

from typing import List

import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks: List[dict] = []
    proved_all = True

    # Let
    #   A_n = a x^n + b y^n.
    # From the given equations, A_1=3, A_2=7, A_3=16, A_4=42.
    # Since A_n satisfies the recurrence A_n = (x+y)A_{n-1} - xy A_{n-2},
    # we have
    #   A_3 = S*A_2 - P*A_1
    #   A_4 = S*A_3 - P*A_2
    # where S = x+y and P = xy.
    # Solving gives S=14 and P=38.
    S, P = Reals("S P")
    try:
        kd.prove(
            ForAll(
                [S, P],
                Implies(
                    And(7 * S - 3 * P == 16, 16 * S - 7 * P == 42),
                    And(S == 14, P == 38),
                ),
            )
        )
        checks.append(
            {
                "name": "derive_S_and_P",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "Derived S=14 and P=38 from the linear system.",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "derive_S_and_P",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to verify derivation of S and P: {type(e).__name__}: {e}",
            }
        )

    # Then
    #   A_5 = S*A_4 - P*A_3 = 14*42 - 38*16 = 20.
    try:
        kd.prove(14 * 42 - 38 * 16 == 20)
        checks.append(
            {
                "name": "compute_ax5_plus_by5",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "Computed ax^5 + by^5 = 20.",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "compute_ax5_plus_by5",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to verify computation of ax^5 + by^5: {type(e).__name__}: {e}",
            }
        )

    return {"proved_all": proved_all, "checks": checks}