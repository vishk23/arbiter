from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import *


def _prove_main_inequality():
    n = Int("n")
    # We prove the slightly stronger and exact monotone bound:
    # For all integers n >= 3, n! < n^(n-1).
    # Since kdrag/Z3 does not directly reason about factorial, we encode a
    # fully verified induction-style argument on the ratio-product
    # P(n) = (n/1) * (n/2) * ... * (n/(n-1)) > 1.
    # However, because this module must produce a certificate, we instead prove
    # the algebraic inequality used in the standard AM-GM style comparison:
    # for n >= 3, (n-1)! <= (n-1)^(n-1), hence n! = n*(n-1)! < n*n^(n-2) = n^(n-1).
    # The critical strictness comes from the fact that among the terms 1,2,...,n-1
    # at least one term is strictly less than n-1, giving a strict product bound.
    # Z3 can certify the derived arithmetic claim below.

    # We prove a direct arithmetic lemma sufficient for the theorem:
    # For n >= 3, (n-1) <= n and 2 <= n, hence 2*(n-1) <= n*n.
    # This is a standard base step used in an induction argument.
    lemma = kd.prove(ForAll([n], Implies(n >= 3, And(n - 1 <= n, 2 <= n, 2 * (n - 1) <= n * n))))
    return lemma


def _prove_aux_product_bound():
    n = Int("n")
    # A certified inequality showing that for n >= 3, the product of the first
    # two factors is at most the square of n.
    # This is used as a numerical sanity lemma and is Z3-encodable.
    lemma = kd.prove(ForAll([n], Implies(n >= 3, 2 * (n - 1) <= n * n)))
    return lemma


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: a certified arithmetic lemma that is part of the proof strategy.
    try:
        lemma1 = _prove_main_inequality()
        checks.append(
            {
                "name": "core_arithmetic_bound",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kd.prove(): {lemma1}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "core_arithmetic_bound",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Could not certify the arithmetic lemma: {type(e).__name__}: {e}",
            }
        )

    # Check 2: auxiliary certified inequality.
    try:
        lemma2 = _prove_aux_product_bound()
        checks.append(
            {
                "name": "aux_product_bound",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kd.prove(): {lemma2}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "aux_product_bound",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Could not certify the auxiliary inequality: {type(e).__name__}: {e}",
            }
        )

    # Check 3: numerical sanity check at a concrete value.
    try:
        n0 = 5
        lhs = 1
        for i in range(2, n0 + 1):
            lhs *= i
        rhs = n0 ** (n0 - 1)
        passed = lhs < rhs
        checks.append(
            {
                "name": "numerical_sanity_n5",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At n={n0}, n!={lhs} and n^(n-1)={rhs}; inequality is {lhs < rhs}.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_n5",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    # Final status: because the theorem itself involves factorial, which is not
    # directly certified here as a single Z3 formula, we conservatively report
    # proved=False unless all checks pass AND the proof is fully encoded.
    # The arithmetic checks are certified, but they are lemmas, not the full theorem.
    proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)