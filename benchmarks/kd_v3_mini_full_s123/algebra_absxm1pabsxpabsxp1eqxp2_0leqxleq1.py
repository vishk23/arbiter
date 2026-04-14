import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved = True

    x = Real("x")

    # Verified theorem: the condition implies 0 <= x <= 1.
    thm = ForAll(
        [x],
        Implies(
            Abs(x - 1) + Abs(x) + Abs(x + 1) == x + 2,
            And(x >= 0, x <= 1),
        ),
    )

    try:
        proof = kd.prove(thm)
        checks.append(
            {
                "name": "main_implication",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "main_implication",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proof failed in kdrag/Z3: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at a concrete point satisfying the conclusion.
    x0 = 1 / 2
    lhs = abs(x0 - 1) + abs(x0) + abs(x0 + 1)
    rhs = x0 + 2
    num_passed = abs(lhs - rhs) < 1e-12 and 0 <= x0 <= 1
    checks.append(
        {
            "name": "numerical_sanity_at_half",
            "passed": num_passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"At x=1/2, lhs={lhs}, rhs={rhs}, interval_check={0 <= x0 <= 1}",
        }
    )
    proved = proved and num_passed

    # Additional symbolic consistency check: on [0,1], the expression is exactly x+2.
    # This is a direct algebraic simplification check, not the main proof.
    y = Real("y")
    branch_thm = ForAll(
        [y],
        Implies(
            And(y >= 0, y <= 1),
            Abs(y - 1) + Abs(y) + Abs(y + 1) == y + 2,
        ),
    )
    try:
        branch_proof = kd.prove(branch_thm)
        checks.append(
            {
                "name": "interval_identity_on_0_1",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned proof: {branch_proof}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "interval_identity_on_0_1",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Branch identity proof failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)