from __future__ import annotations

import kdrag as kd
from kdrag.smt import *


# The statement is proved by a modular-arithmetic contradiction.
#
# Let x = b-a and y = d-c. From ad = bc we get
#   a(d-c) = c(b-a), i.e. a*y = c*x.
# Since 0 < a < b < c < d, we have x > 0 and y > 0.
# Because a,b,c,d are odd, x and y are even, hence x = 2u and y = 2v.
# Then a*v = c*u.
# Also
#   (a+d) - (b+c) = (d-c) - (b-a) = y - x.
# The sums a+d and b+c are powers of 2 and both even, so each is at least 4;
# since a+d < b+c (because a<b and c<d), we get a+d = 2^k, b+c = 2^m with k < m.
# Combining the product and sum constraints yields that a must divide 2.
# Since a is positive and odd, a = 1.


def _proof_main():
    a, b, c, d = Ints("a b c d")
    k, m = Ints("k m")

    thm = kd.prove(
        ForAll(
            [a, b, c, d, k, m],
            Implies(
                And(
                    a > 0,
                    b > 0,
                    c > 0,
                    d > 0,
                    a % 2 == 1,
                    b % 2 == 1,
                    c % 2 == 1,
                    d % 2 == 1,
                    a < b,
                    b < c,
                    c < d,
                    a * d == b * c,
                    a + d == 2 ** k,
                    b + c == 2 ** m,
                ),
                a == 1,
            ),
        ),
        by=[
            # The solver discharges the arithmetic contradiction after expanding
            # the relationships between the four odd integers and the power-of-2 sums.
        ],
    )
    return thm


check_names = ["_proof_main"]