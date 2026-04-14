from math import gcd

import kdrag as kd
from kdrag.smt import *


def h_value(x: int) -> int:
    return gcd(12 * x + 7, 5 * x + 2)


def possible_h_values_bound() -> tuple[bool, str]:
    """Numerical sanity check on a few concrete x values."""
    samples = {x: h_value(x) for x in [1, 2, 3, 4, 5, 15, 16, 27]}
    observed = set(samples.values())
    ok = observed.issubset({1, 11}) and 1 in observed and 11 in observed
    detail = f"samples={samples}, observed_values={sorted(observed)}"
    return ok, detail


def verify() -> dict:
    checks = []
    proved_all = True

    # Check 1: Verified proof that any common divisor of 12x+7 and 5x+2 divides 11.
    x = Int("x")
    a = 12 * x + 7
    b = 5 * x + 2
    d = Int("d")
    try:
        thm_divides_11 = kd.prove(
            ForAll(
                [x, d],
                Implies(
                    And(x >= 1, d > 0, d == gcd(a, b)),
                    Or(d == 1, d == 11),
                ),
            )
        )
        checks.append(
            {
                "name": "gcd_values_are_only_1_or_11",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {thm_divides_11}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "gcd_values_are_only_1_or_11",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed or gcd is not directly encodable in Z3 as used here: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Symbolic/numerical confirmation of the Euclidean algorithm reduction.
    # We verify the algebraic equalities on concrete integers and with a symbolic identity.
    try:
        n = Int("n")
        lhs1 = (12 * n + 7) - 2 * (5 * n + 2)
        lhs2 = (5 * n + 2) - 2 * (2 * n + 3)
        lhs3 = (2 * n + 3) - 2 * (n - 4)
        euclid_identity = kd.prove(
            ForAll([n], And(lhs1 == 2 * n + 3, lhs2 == n - 4, lhs3 == 11))
        )
        checks.append(
            {
                "name": "euclidean_reduction_identity",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove succeeded: {euclid_identity}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "euclidean_reduction_identity",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to certify Euclidean reduction: {type(e).__name__}: {e}",
            }
        )

    # Check 3: Numerical sanity check.
    ok_num, detail_num = possible_h_values_bound()
    checks.append(
        {
            "name": "numerical_sanity_check",
            "passed": ok_num,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": detail_num,
        }
    )
    if not ok_num:
        proved_all = False

    # Final mathematical claim: possible values are 1 and 11, so sum is 12.
    # If the above certificates fail due to backend limitations, we do not fake the proof.
    if proved_all:
        final_details = "Verified that h(x) can only take the values 1 and 11; therefore their sum is 12."
    else:
        final_details = (
            "Not all checks could be certified in this environment. The intended proof is via "
            "the Euclidean algorithm: gcd(12x+7,5x+2)=gcd(x-4,11), so h(x) is 1 or 11, and the sum is 12."
        )

    checks.append(
        {
            "name": "final_conclusion",
            "passed": proved_all,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": final_details,
        }
    )

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    import json

    print(json.dumps(verify(), indent=2))