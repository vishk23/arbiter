import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Main verified proof: for all real a, a(2-a) <= 1.
    a = Real("a")
    thm = None
    try:
        thm = kd.prove(ForAll([a], a * (2 - a) <= 1))
        checks.append(
            {
                "name": "main_inequality_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned a proof: {thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "main_inequality_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity checks at concrete values.
    test_vals = [0, 1, 2, -3, 1.5]
    num_passed = True
    details = []
    for v in test_vals:
        lhs = v * (2 - v)
        ok = lhs <= 1 + 1e-12
        num_passed = num_passed and ok
        details.append(f"a={v}: a(2-a)={lhs}")
    checks.append(
        {
            "name": "numerical_sanity_checks",
            "passed": num_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": "; ".join(details),
        }
    )

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)