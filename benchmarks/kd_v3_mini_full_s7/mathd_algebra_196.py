import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified proof: any integer x satisfying |2-x| = 3 must be one of two cases.
    # We formalize the theorem over reals, since the equation is real-valued.
    x = Real("x")
    thm = None
    try:
        thm = kd.prove(
            ForAll(
                [x],
                Implies(
                    Abs(2 - x) == 3,
                    Or(And(x == -1), And(x == 5))
                ),
            )
        )
        checks.append(
            {
                "name": "absolute_value_cases_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proved that |2-x|=3 implies x=-1 or x=5. Proof: {thm}",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "absolute_value_cases_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete solutions.
    try:
        sanity = (abs(2 - (-1)) == 3) and (abs(2 - 5) == 3) and ((-1) + 5 == 4)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": bool(sanity),
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Checked that x=-1 and x=5 satisfy |2-x|=3 and their sum is 4.",
            }
        )
    except Exception as e:
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical check failed: {type(e).__name__}: {e}",
            }
        )

    # Derived conclusion: sum of all solutions is 4.
    all_passed = all(ch["passed"] for ch in checks)
    if all_passed:
        details = "The only solutions are x=-1 and x=5, so their sum is 4."
    else:
        details = "One or more checks failed; cannot certify the final theorem."

    checks.append(
        {
            "name": "final_answer",
            "passed": all_passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": details,
        }
    )

    return {"proved": all_passed, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)