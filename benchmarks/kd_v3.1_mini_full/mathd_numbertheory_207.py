import kdrag as kd
from kdrag.smt import Int, ForAll, Implies


def verify():
    checks = []

    # Verified proof: place-value evaluation of 852_9 equals 695.
    # We prove the concrete arithmetic equality using kdrag/Z3.
    try:
        thm = kd.prove(8 * 9**2 + 5 * 9 + 2 == 695)
        checks.append({
            "name": "base9_to_base10_concrete_evaluation",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved concrete equality with certificate: {thm}",
        })
    except Exception as e:
        checks.append({
            "name": "base9_to_base10_concrete_evaluation",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })

    # Numerical sanity check
    value = 8 * 9**2 + 5 * 9 + 2
    checks.append({
        "name": "numerical_sanity_check",
        "passed": (value == 695),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed 8*9**2 + 5*9 + 2 = {value}",
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)