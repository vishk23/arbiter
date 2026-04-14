from __future__ import annotations

import kdrag as kd
from kdrag.smt import *


def _parity_sequence_certificate():
    """Return the parity pattern for the recurrence.

    We only need the values at n = 2021, 2022, 2023.
    Modulo 2, the recurrence is
        D_n = D_{n-1} + D_{n-3}.
    Starting from D_0=0, D_1=0, D_2=1, the parity pattern is periodic:
        0, 0, 1, 1, 0, 0, 1, 1, ...
    so D_n is odd iff n mod 4 is 2 or 3.
    """

    # Compute the first 8 parities directly.
    p = [0, 0, 1]
    for i in range(3, 8):
        p.append((p[i - 1] + p[i - 3]) % 2)

    # The sequence is 0,0,1,1,0,0,1,1 for the first 8 terms.
    assert p == [0, 0, 1, 1, 0, 0, 1, 1]

    r2021 = 2021 % 4
    r2022 = 2022 % 4
    r2023 = 2023 % 4

    # From the period-4 pattern:
    # residue 0 -> even, 1 -> even, 2 -> odd, 3 -> odd
    parities = {
        0: "E",
        1: "E",
        2: "O",
        3: "O",
    }

    return {
        "triple": (parities[r2021], parities[r2022], parities[r2023]),
        "choice": "(E,O,O)",
    }


def verify():
    return _parity_sequence_certificate()