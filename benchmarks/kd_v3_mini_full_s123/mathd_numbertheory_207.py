import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified proof: arithmetic evaluation in Z3/kdrag.
    # Statement: 8*9^2 + 5*9 + 2 = 695.
    try:
        thm = kd.prove(8 * 9 * 9 + 5 * 9 + 2 == 695)
        checks.append({
            "name": "base9_to_base10_exact_value",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}",
        })
    except Exception as e:
        checks.append({
            "name": "base9_to_base10_exact_value",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check
    expr_val = 8 * 9**2 + 5 * 9 + 2
    checks.append({
        "name": "numerical_sanity_check",
        "passed": (expr_val == 695),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Evaluated 8*9**2 + 5*9 + 2 = {expr_val}",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)