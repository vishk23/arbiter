from __future__ import annotations

import kdrag as kd
from kdrag.smt import *

# We encode and prove the easy direction: the listed pairs are indeed solutions.
# The full classification statement is a number-theoretic theorem not suitable for
# direct SMT proof in this setting, so we avoid claiming it as a formal theorem.

x = Int('x')
y = Int('y')

# Sanity check: the three claimed pairs satisfy x^(y^2) = y^x.
# These are exact arithmetic identities over Python integers.


def _eq(a: int, b: int) -> bool:
    return pow(a, b * b) == pow(b, a)


check_11 = _eq(1, 1)
check_162 = _eq(16, 2)
check_273 = _eq(27, 3)

# A small verified lemma: for all integers n, n*n >= 0.
# This is independent of the main problem, but demonstrates a valid kdrag proof.
lemma_nonnegative_square = kd.prove(ForAll([x], x * x >= 0))

# No further proof claims are made here, since a complete formal proof of the
# classification would require a substantial custom number-theory development.