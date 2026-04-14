import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Certified proof: the base-9 expansion equals 695.
    expr = 8 * 9**2 + 5 * 9 + 2
    try:
        proof = kd.prove(expr == 695)
        checks.append({
            "name": "base9_expression_equals_695",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove certified that 8*9^2 + 5*9 + 2 = 695; proof={proof}",
        })
    except Exception as e:
        checks.append({
            "name": "base9_expression_equals_695",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at concrete values.
    numeric_value = 8 * (9 ** 2) + 5 * 9 + 2
    checks.append({
        "name": "numerical_evaluation",
        "passed": numeric_value == 695,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed 8*(9**2) + 5*9 + 2 = {numeric_value}.",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())