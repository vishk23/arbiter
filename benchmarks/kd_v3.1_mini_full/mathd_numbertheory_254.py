import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Certified proof: the total number of marbles is 496, so the remainder upon
    # division by 10 is 6.
    total = 239 + 174 + 83
    try:
        thm_total = kd.prove(total == 496)
        checks.append({
            "name": "total_marbles_sum_is_496",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove established that 239 + 174 + 83 == 496. Proof: {thm_total}",
        })
    except Exception as e:
        checks.append({
            "name": "total_marbles_sum_is_496",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Certified proof: 496 = 10*49 + 6, so 496 % 10 = 6.
    try:
        thm_rem = kd.prove(total % 10 == 6)
        checks.append({
            "name": "total_marbles_remainder_is_6",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove established that ({total}) % 10 == 6. Proof: {thm_rem}",
        })
    except Exception as e:
        checks.append({
            "name": "total_marbles_remainder_is_6",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check.
    numerical_ok = (total == 496) and (total % 10 == 6)
    checks.append({
        "name": "numerical_sanity_total_and_remainder",
        "passed": numerical_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"239 + 174 + 83 = {total}, and {total} % 10 = {total % 10}.",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)