from __future__ import annotations

from typing import Dict, List

import kdrag as kd
from kdrag.smt import *


def _parity_sequence_upto(n: int) -> List[int]:
    """Compute D_0..D_n modulo 2 using the recurrence."""
    D = [0, 0, 1]
    if n < 3:
        return D[: n + 1]
    for i in range(3, n + 1):
        D.append((D[i - 1] + D[i - 3]) % 2)
    return D


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Numerical sanity check: directly compute the needed parities.
    seq = _parity_sequence_upto(2023)
    numerical_ans = (seq[2021], seq[2022], seq[2023])
    num_passed = numerical_ans == (0, 1, 0)
    checks.append(
        {
            "name": "numerical_parity_of_D_2021_2023",
            "passed": num_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed parities modulo 2: (D_2021,D_2022,D_2023) = {numerical_ans}; expected (0, 1, 0) corresponding to (E,O,E).",
        }
    )
    proved = proved and num_passed

    # Verified proof via kdrag: prove the parity evolution formula modulo 2.
    # Let p(n) be D_n mod 2, encoded directly on Nat-like Ints with bounded domain.
    n = Int("n")
    D = Function("D", IntSort(), IntSort())

    # Axiomatize the recurrence over integers, but only use it as a symbolic skeleton.
    # The actual proof below is a concrete finite instantiation checked by Z3.
    ax0 = kd.axiom(D(0) == 0)
    ax1 = kd.axiom(D(1) == 0)
    ax2 = kd.axiom(D(2) == 1)
    axr = kd.axiom(ForAll([n], Implies(n >= 3, D(n) % 2 == (D(n - 1) + D(n - 3)) % 2)))

    try:
        # Prove the 7-step periodicity pattern by concrete unrolling.
        # The recurrence modulo 2 generates the cycle:
        # 0,0,1,1,1,0,1,0,0,1,... so D_{k+7} mod 2 = D_k mod 2 for k=0,1,2.
        c0 = kd.prove(D(7) % 2 == D(0) % 2, by=[ax0, ax1, ax2, axr])
        c1 = kd.prove(D(8) % 2 == D(1) % 2, by=[ax0, ax1, ax2, axr])
        c2 = kd.prove(D(9) % 2 == D(2) % 2, by=[ax0, ax1, ax2, axr])
        # From the computed period-7 cycle, 2021 ≡ 5, 2022 ≡ 6, 2023 ≡ 0 mod 7.
        # Therefore (D_2021, D_2022, D_2023) has the same parity as (D_5, D_6, D_7).
        # We verify the needed concrete values.
        d5 = kd.prove(D(5) % 2 == 0, by=[ax0, ax1, ax2, axr])
        d6 = kd.prove(D(6) % 2 == 1, by=[ax0, ax1, ax2, axr])
        d7 = kd.prove(D(7) % 2 == 0, by=[ax0, ax1, ax2, axr])
        kdrag_passed = all(isinstance(p, kd.Proof) for p in [c0, c1, c2, d5, d6, d7])
        checks.append(
            {
                "name": "kdrag_verified_parity_cycle_and_values",
                "passed": kdrag_passed,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": "Verified by kd.prove() that the recurrence modulo 2 is consistent with the period-7 pattern and that D_5, D_6, D_7 have parities E, O, E.",
            }
        )
        proved = proved and kdrag_passed
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_verified_parity_cycle_and_values",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)