from __future__ import annotations

from fractions import Fraction
from typing import Any, Dict, List

import kdrag as kd
from kdrag.smt import *


# The theorem is about a finite product of positive rational terms.
# We prove a stronger inductive statement over integers n >= 3:
#   P(n): prod_{k=1}^n (1 + 1/2^k) < 5/2 * (1 - 1/2^n)
# This implies the target bound < 5/2 immediately.


def _product_term(k: int) -> Fraction:
    return Fraction(1, 1) + Fraction(1, 2 ** k)


def _python_product(n: int) -> Fraction:
    p = Fraction(1, 1)
    for k in range(1, n + 1):
        p *= _product_term(k)
    return p


def verify() -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []
    proved = True

    # Numerical sanity checks
    for n in [1, 2, 3, 4, 5]:
        lhs = _python_product(n)
        rhs = Fraction(5, 2)
        passed = lhs < rhs
        checks.append(
            {
                "name": f"numerical_sanity_n_{n}",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"lhs={lhs}, rhs={rhs}, strict inequality holds={passed}",
            }
        )
        proved = proved and passed

    # Verified proof of the base case n = 3 for the stronger statement.
    # Exact rational arithmetic:
    # (1+1/2)(1+1/4)(1+1/8)=135/64 < 35/16 = 5/2*(1-1/8)
    try:
        base_lhs = Fraction(135, 64)
        base_rhs = Fraction(35, 16)
        base_passed = base_lhs < base_rhs
        checks.append(
            {
                "name": "base_case_stronger_n_3",
                "passed": base_passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Exact check: 135/64 < 35/16 is {base_passed}",
            }
        )
        proved = proved and base_passed
    except Exception as e:
        checks.append(
            {
                "name": "base_case_stronger_n_3",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Exception during exact arithmetic check: {e}",
            }
        )
        proved = False

    # kdrag proof: a key algebraic inequality used in the induction step.
    # For x = 2^(n+1) >= 2, we have:
    #   (1 - 1/x)(1 + 1/(2x)) = 1 - 1/(2x) - 1/(2x^2) < 1 - 1/(2x)
    # In integer form, if x > 0 then (x-1)(2x+1) < 2x(x-1? )
    # Rather than force a complicated universal quantifier, we prove a concrete
    # instance sufficient as a certificate of the algebraic step for x=2^m.
    try:
        x = Int("x")
        algebraic_step = kd.prove(
            ForAll([x], Implies(x >= 2, (x - 1) * (2 * x + 1) < 2 * x * (x + 1)))
        )
        checks.append(
            {
                "name": "kdrag_algebraic_inequality",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(algebraic_step),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "kdrag_algebraic_inequality",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag could not certify the auxiliary inequality: {e}",
            }
        )
        proved = False

    # Since a full induction over a custom finite product is cumbersome to encode
    # directly in Z3 without additional recursive definitions, we rely on the
    # exact base case and numerical sanity checks, while reporting the limitation.
    # The theorem itself is true, but this module only certifies the auxiliary facts.
    if not any(c["passed"] and c["proof_type"] == "certificate" for c in checks):
        proved = False

    # The overall theorem is not fully discharged inside kdrag here; we record that honestly.
    # However, the certified auxiliary check above is a genuine proof certificate.
    proved = False

    checks.append(
        {
            "name": "global_status",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "A full formal induction over the finite product was not encoded in this module; only auxiliary certified facts and numerical checks were produced.",
        }
    )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2, default=str))