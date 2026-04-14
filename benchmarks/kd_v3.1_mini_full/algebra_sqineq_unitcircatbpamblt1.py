import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Main verified proof via kdrag/Z3:
    # From (a - b - 1)^2 >= 0 and a^2 + b^2 = 1,
    # derive 1 - (ab + a - b) >= 0, hence ab + (a - b) <= 1.
    a, b = Reals("a b")

    thm = None
    try:
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
                "details": f"Verified by Z3 certificate: {thm}",
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
                "details": f"Proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete feasible point.
    # Example: a = 1, b = 0 satisfies a^2 + b^2 = 1 and gives ab + a - b = 1.
    try:
        aval = 1.0
        bval = 0.0
        lhs = aval * bval + (aval - bval)
        rhs = 1.0
        passed_num = abs(aval * aval + bval * bval - 1.0) < 1e-12 and lhs <= rhs + 1e-12
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed_num,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"At (a,b)=({aval},{bval}), constraint={aval*aval + bval*bval}, lhs={lhs}, rhs={rhs}.",
            }
        )
        if not passed_num:
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

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)