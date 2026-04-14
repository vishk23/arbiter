import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Main verified proof: forall real a, a(2-a) <= 1
    a = Real("a")
    theorem = ForAll([a], a * (2 - a) <= 1)
    try:
        proof = kd.prove(theorem)
        checks.append({
            "name": "universal_quadratic_inequality",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved by Z3-backed certificate: {proof}",
        })
    except Exception as e:
        checks.append({
            "name": "universal_quadratic_inequality",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag failed to prove the theorem: {e}",
        })

    # Numerical sanity check at a concrete value
    try:
        a0 = 3.0
        lhs = a0 * (2 - a0)
        rhs = 1.0
        passed = lhs <= rhs + 1e-12
        checks.append({
            "name": "numerical_sanity_at_a_equals_3",
            "passed": bool(passed),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At a={a0}, a(2-a)={lhs}, and 1={rhs}.",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_at_a_equals_3",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)