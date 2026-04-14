from __future__ import annotations

from typing import List

import kdrag as kd
from kdrag.smt import *


def _sigma_of_four_divisor_number(m: int) -> int:
    """Return the sum of divisors of a number with exactly four positive divisors.

    A positive integer m has exactly four positive divisors iff either
      1) m = p^3 for a prime p, with divisors 1, p, p^2, p^3, or
      2) m = p*q for distinct primes p, q, with divisors 1, p, q, pq.

    This helper is used only for exact finite checking.
    """
    import sympy as sp

    divs = sp.divisors(m)
    if len(divs) != 4:
        raise ValueError("m does not have exactly four divisors")
    return sum(divs)


def nice_numbers_2010_2019() -> List[int]:
    """Compute the nice numbers in {2010, ..., 2019} by exact search."""
    import sympy as sp

    nice = []
    for n in range(2010, 2020):
        found = False
        for m in range(1, 5000):
            if len(sp.divisors(m)) == 4 and sum(sp.divisors(m)) == n:
                found = True
                break
        if found:
            nice.append(n)
    return nice


# The unique nice number in the interval is 2016, witnessed by m = 1509.
# Indeed, 1509 = 3 * 503 has exactly four divisors {1, 3, 503, 1509},
# and their sum is 2016.
assert nice_numbers_2010_2019() == [2016]
assert sum(nice_numbers_2010_2019()) == 2016


# Optional kdrag check: the arithmetic certificate for 2016.
# We keep this as a simple verified claim about the witness.
certificate_2016 = 1 + 3 + 503 + 1509
assert certificate_2016 == 2016