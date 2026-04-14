from sympy import symbols
import kdrag as kd
from kdrag.smt import Real, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Check 1: Verified formal proof in kdrag/Z3.
    try:
        a = Real("a")
        b = Real("b")
        thm = kd.prove(
            ForAll(
                [a, b],
                Implies(
                    a * a + b * b == 1,
                    a * b + (a - b) <= 1,
                ),
            )
        )
        checks.append(
            {
                "name": "main_inequality_proof",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified by kd.prove(): {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "main_inequality_proof",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: Numerical sanity check at a concrete point on the unit circle.
    try:
        a_val = 3 / 5
        b_val = 4 / 5
        lhs = a_val * b_val + (a_val - b_val)
        passed = lhs <= 1 + 1e-12
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(passed),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At (a,b)=({a_val},{b_val}), lhs={lhs} and lhs<=1 is {passed}.",
            }
        )
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)