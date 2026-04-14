from __future__ import annotations

import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And, Not


def verify() -> dict:
    checks = []

    # Verified proof: 116 is an inverse of 24 modulo 11^2 = 121.
    try:
        b = Int("b")
        thm = kd.prove(
            (24 * 116) % 121 == 1,
        )
        checks.append(
            {
                "name": "24_times_116_congruent_1_mod_121",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove certified that 24*116 ≡ 1 (mod 121): {thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "24_times_116_congruent_1_mod_121",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check: direct computation.
    b_val = 116
    num_pass = (24 * b_val) % (11 ** 2) == 1 and 0 <= b_val < 11 ** 2
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": bool(num_pass),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed (24*{b_val}) % 121 = {(24*b_val) % 121}; range check 0 <= {b_val} < 121 is {0 <= b_val < 121}.",
        }
    )

    # Uniqueness / correctness check: show the proposed residue is exactly 116.
    # This is a computational check that 24*116 = 121*23 + 1.
    lhs = 24 * 116
    rhs = 121 * 23 + 1
    checks.append(
        {
            "name": "exact_integer_identity",
            "passed": lhs == rhs,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Verified exact identity 24*116 = {lhs} and 121*23 + 1 = {rhs}.",
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)