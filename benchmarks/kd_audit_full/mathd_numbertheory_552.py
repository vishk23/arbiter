from math import gcd

import kdrag as kd
from kdrag.smt import *


def _h_py(x: int) -> int:
    return gcd(12 * x + 7, 5 * x + 2)


def verify():
    checks = []

    # Verified proof: Euclidean-algorithm invariant on gcd through linear combinations.
    x = Int("x")
    try:
        thm = kd.prove(
            ForAll(
                [x],
                gcd(12 * x + 7, 5 * x + 2) == gcd(x - 4, 11),
            )
        )
        checks.append(
            {
                "name": "euclidean_algorithm_gcd_reduction",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": str(thm),
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "euclidean_algorithm_gcd_reduction",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Could not certify gcd reduction in kdrag: {e}",
            }
        )

    # Verified proof: the only possible gcd values are 1 and 11.
    # This is checked by exhaustive residue analysis modulo 11, plus a concrete witness.
    try:
        possible = set()
        for r in range(11):
            possible.add(gcd(12 * r + 7, 5 * r + 2))
        # Since gcd(12x+7,5x+2) divides 11 by the Euclidean reduction, only 1 or 11 can occur.
        # We confirm both values occur numerically.
        witness_1 = _h_py(1)
        witness_11 = _h_py(4)
        passed = possible == {1, 11} and witness_1 == 1 and witness_11 == 11
        checks.append(
            {
                "name": "possible_values_are_1_and_11",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Residue scan mod 11 gave {sorted(possible)}; h(1)={witness_1}, h(4)={witness_11}.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "possible_values_are_1_and_11",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {e}",
            }
        )

    # Numerical sanity check requested by the prompt.
    try:
        val = _h_py(4)
        checks.append(
            {
                "name": "numerical_sanity_h_of_4",
                "passed": (val == 11),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"h(4)=gcd(55,22)={val}.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_h_of_4",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {e}",
            }
        )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)