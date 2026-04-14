from __future__ import annotations

from typing import List

from sympy import binomial

# Numerical helper to compute the target sum exactly.
def sum_expression(n: int) -> int:
    return sum(int(binomial(2 * n + 1, 2 * k + 1)) * (2 ** (3 * k)) for k in range(n + 1))


# Verify the claimed property computationally for a finite range.
def target_not_divisible_by_5(n: int) -> bool:
    return sum_expression(n) % 5 != 0


# Small sample values for quick sanity checking.
checked_samples: List[bool] = [target_not_divisible_by_5(n) for n in range(8)]


# Additional numerical sanity check.
def numerical_sanity(limit: int = 10) -> bool:
    return all(target_not_divisible_by_5(n) for n in range(limit))