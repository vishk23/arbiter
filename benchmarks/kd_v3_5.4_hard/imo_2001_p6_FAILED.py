import traceback
import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    K, L, M, N = Ints("K L M N")

    hyp = And(
        K > L,
        L > M,
        M > N,
        N > 0,
        K * M + L * N == (K + L - M + N) * (-K + L + M + N),
    )

    # Expand the RHS:
    # (K+L-M+N)(-K+L+M+N) = -K^2 + L^2 + 2KM - M^2 + 2LN + N^2
    # So the hypothesis implies
    #   KM + LN = -K^2 + L^2 + 2KM - M^2 + 2LN + N^2
    # hence
    #   K^2 - KM + M^2 = L^2 + LN + N^2.
    # Therefore
    #   K(K-M) + M^2 = L^2 + LN + N^2.
    # Since K > L > M, we have K-M > L-M > 0.
    # Search for the actual structure by setting
    #   a = K-L > 0, b = L-M > 0, c = M-N > 0.
    # Then K = N+a+b+c, L = N+b+c, M = N+c.
    # Substituting yields
    #   2ab + a*c + b*c + c^2 = N(a+b-c).
    # A simpler direct rearrangement in terms of K gives a linear formula:
    #   K(M+L+N-K) = (L+N-M)(L+M+N).
    # We verify the key consequence K = L + N and M = L - N by proving the final
    # factorization directly from the hypothesis.

    # Check 1: prove KL + MN = (K-N)(M+N).
    # This follows from the given equation after algebraic elimination:
    # from
    #   K^2 - KM + M^2 = L^2 + LN + N^2
    # one gets
    #   KL + MN = KM + KN - MN - N^2 = (K-N)(M+N),
    # under the same defining relation. We ask the solver to certify it.
    try:
        thm = kd.prove(ForAll([K, L, M, N], Implies(hyp, KL + MN == (K - N) * (M + N))))
        checks.append({
            "name": "kdrag_factorization_KL_plus_MN",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "kdrag_factorization_KL_plus_MN",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": traceback.format_exc(),
        })

    # Check 2: prove both factors are > 1, hence KL+MN is composite and not prime.
    try:
        thm1 = kd.prove(ForAll([K, L, M, N], Implies(hyp, K - N > 1)))
        thm2 = kd.prove(ForAll([K, L, M, N], Implies(hyp, M + N > 1)))
        checks.append({
            "name": "kdrag_nontrivial_factors",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str((thm1, thm2)),
        })
    except Exception:
        proved = False
        checks.append({
            "name": "kdrag_nontrivial_factors",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": traceback.format_exc(),
        })

    # Check 3: direct existential non-primality witness via factorization.
    # There exist integers a,b with a>1, b>1 and KL+MN = a*b.
    try:
        a, b = Ints("a b")
        thm = kd.prove(
            ForAll(
                [K, L, M, N],
                Implies(
                    hyp,
                    Exists(
                        [a, b],
                        And(a > 1, b > 1, KL + MN == a * b, a == K - N, b == M + N),
                    ),
                ),
            )
        )
        checks.append({
            "name": "kdrag_exists_composite_factorization",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        })
    except Exception:
        proved = False
        checks.append({
            "name": "kdrag_exists_composite_factorization",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": traceback.format_exc(),
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())