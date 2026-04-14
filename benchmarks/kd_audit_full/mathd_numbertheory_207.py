from typing import Dict, List

import kdrag as kd
from kdrag.smt import Ints, Solver, sat


def _base9_to_base10_value() -> int:
    # Exact arithmetic for 852_9 = 8*9^2 + 5*9 + 2
    return 8 * (9 ** 2) + 5 * 9 + 2


def verify() -> Dict[str, object]:
    checks: List[Dict[str, object]] = []
    proved = True

    # Verified proof: use kdrag to prove the arithmetic identity exactly.
    try:
        a, b, c = Ints("a b c")
        # Instantiate the specific numeral expression for base-9 conversion.
        thm = kd.prove((8 * (9 ** 2) + 5 * 9 + 2) == 695)
        checks.append({
            "name": "base9_conversion_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "base9_conversion_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at concrete values.
    val = _base9_to_base10_value()
    num_passed = (val == 695)
    checks.append({
        "name": "numerical_sanity_check",
        "passed": num_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed 8*9^2 + 5*9 + 2 = {val}",
    })
    proved = proved and num_passed

    # A second exact arithmetic check, purely computational but deterministic.
    decomposition = 8 * 81 + 5 * 9 + 2
    decomp_passed = (decomposition == 695)
    checks.append({
        "name": "expanded_decomposition_check",
        "passed": decomp_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Expanded form 8*81 + 5*9 + 2 = {decomposition}",
    })
    proved = proved and decomp_passed

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)