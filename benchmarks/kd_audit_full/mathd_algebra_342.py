from fractions import Fraction

import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: solve the linear system derived from the arithmetic series sums.
    a, d = Reals("a d")
    thm_name = "first_term_equals_42_over_5"
    try:
        proof = kd.prove(
            ForAll(
                [a, d],
                Implies(
                    And(5 * a + 10 * d == 70, 10 * a + 45 * d == 210),
                    a == RealVal("42/5"),
                ),
            )
        )
        checks.append(
            {
                "name": thm_name,
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned a proof object: {proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": thm_name,
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check.
    a_val = Fraction(42, 5)
    d_val = Fraction(7, 5)
    s5 = 5 * a_val + 10 * d_val
    s10 = 10 * a_val + 45 * d_val
    numeric_passed = (s5 == 70) and (s10 == 210)
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": numeric_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Using a=42/5, d=7/5 gives S5={s5}, S10={s10}.",
        }
    )
    if not numeric_passed:
        proved = False

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)