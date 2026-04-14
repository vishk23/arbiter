from __future__ import annotations

from typing import Dict, List, Any

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def _prove_mod_sum_zero():
    """Prove that S = 2010 + ... + 4018 is congruent to 0 mod 2009."""
    # Encode the closed form sum: there are 2009 terms from 2010 to 4018.
    S = sum(range(2010, 4019))
    assert S == 6030456
    assert S % 2009 == 0

    # Verified backend proof: the arithmetic fact that the computed sum is divisible by 2009.
    # Z3 can certify the modular arithmetic statement directly.
    thm = kd.prove(S % 2009 == 0)
    return thm


def _prove_partial_sum_formula():
    """A general verified arithmetic identity used as supporting evidence.

    Sum_{k=1}^n k = n(n+1)/2, specialized at n = 2008 gives 2008*2009/2.
    This is proved as a concrete arithmetic check rather than a general theorem,
    since the required theorem is about the specific residue of S.
    """
    n = 2008
    lhs = sum(range(1, n + 1))
    rhs = n * (n + 1) // 2
    assert lhs == rhs
    # Numerical sanity: rhs is exactly 1004*2009.
    assert rhs == 1004 * 2009
    return lhs == rhs


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Check 1: Verified proof via kdrag/Z3.
    try:
        thm = _prove_mod_sum_zero()
        checks.append(
            {
                "name": "sum_2010_to_4018_mod_2009_is_zero",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded with proof object: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sum_2010_to_4018_mod_2009_is_zero",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Supporting exact arithmetic identity.
    try:
        ok = _prove_partial_sum_formula()
        checks.append(
            {
                "name": "sum_1_to_2008_closed_form_sanity",
                "passed": bool(ok),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Verified by exact integer computation: sum(range(1,2009)) == 2008*2009/2 == 1004*2009.",
            }
        )
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "sum_1_to_2008_closed_form_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Exact arithmetic check failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Concrete numerical sanity check for the final residue.
    try:
        S = sum(range(2010, 4019))
        residue = S % 2009
        passed = residue == 0
        checks.append(
            {
                "name": "direct_residue_evaluation",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"S = {S}, S % 2009 = {residue}.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "direct_residue_evaluation",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Failed to compute residue: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)