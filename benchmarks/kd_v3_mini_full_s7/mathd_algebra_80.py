import kdrag as kd
from kdrag.smt import *


def verify() -> dict:
    checks = []
    proved_all = True

    # Check 1: Verified proof that the algebraic manipulation implies x = -11.
    # We prove the cross-multiplied equation x - 9 = 2x + 2 implies x = -11.
    x = Int("x")
    theorem = ForAll([x], Implies(x - 9 == 2 * x + 2, x == -11))
    try:
        proof = kd.prove(theorem)
        checks.append({
            "name": "cross_multiplication_implies_x_is_minus_11",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified theorem: {proof}"
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "cross_multiplication_implies_x_is_minus_11",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove theorem in kdrag: {e}"
        })

    # Check 2: Validity of the candidate solution x = -11 in the original equation.
    # This is a concrete numerical sanity check.
    try:
        candidate = -11
        lhs = (candidate - 9) / (candidate + 1)
        passed = (lhs == 2)
        if not passed:
            proved_all = False
        checks.append({
            "name": "candidate_solution_satisfies_original_equation",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For x = -11, LHS = {lhs}, RHS = 2."
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "candidate_solution_satisfies_original_equation",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical evaluation failed: {e}"
        })

    # Check 3: Ensure the denominator is nonzero at the solution.
    try:
        candidate = -11
        denom = candidate + 1
        passed = (denom != 0)
        if not passed:
            proved_all = False
        checks.append({
            "name": "denominator_nonzero_at_solution",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For x = -11, denominator x + 1 = {denom}, so the expression is well-defined."
        })
    except Exception as e:
        proved_all = False
        checks.append({
            "name": "denominator_nonzero_at_solution",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}"
        })

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)