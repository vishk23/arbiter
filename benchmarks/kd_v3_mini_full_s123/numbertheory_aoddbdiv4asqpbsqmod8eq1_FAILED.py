import kdrag as kd
from kdrag.smt import *


# -----------------------------------------------------------------------------
# Theorem:
#   If a is odd and 4 divides b, then a^2 + b^2 ≡ 1 (mod 8).
# -----------------------------------------------------------------------------


def verify():
    checks = []

    a, m, k = Ints("a m k")

    # Encode the assumptions directly in a way Z3 can reason about:
    #   a odd  -> a = 2m + 1
    #   4 | b  -> b = 4k
    # Then compute modulo 8.
    theorem = ForAll(
        [a, m, k],
        Implies(
            And(a == 2 * m + 1),
            ((a * a + (4 * k) * (4 * k)) % 8) == 1,
        ),
    )

    proof = kd.prove(theorem)
    checks.append("kdrag_modular_square_identity")

    return checks


if __name__ == "__main__":
    print(verify())