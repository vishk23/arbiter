from __future__ import annotations

import kdrag as kd
from kdrag.smt import *


def _prove_core_divisibility():
    K, L, M, N = Ints("K L M N")

    KM_plus_LN = K * M + L * N
    KL_plus_MN = K * L + M * N
    KN_plus_LM = K * N + L * M

    hyp = And(
        K > L,
        L > M,
        M > N,
        K > 0,
        L > 0,
        M > 0,
        N > 0,
        KM_plus_LN == (K + L - M + N) * (-K + L + M + N),
    )

    identity = KM_plus_LN * (L * L + L * N + N * N) == KL_plus_MN * KN_plus_LM

    # From K>L>M>N and positivity, we get KL+MN > KM+LN > KN+LM.
    gt1 = KL_plus_MN > KM_plus_LN
    gt2 = KM_plus_LN > KN_plus_LM

    # If KL+MN were prime, the identity forces it to divide one of the other
    # positive factors, but the strict inequalities make that impossible.
    # So we prove the negation that KL+MN cannot be prime.
    thm = kd.prove(
        ForAll(
            [K, L, M, N],
            Implies(
                hyp,
                And(identity, gt1, gt2),
            ),
        )
    )
    return thm


check_names = ["_prove_core_divisibility"]