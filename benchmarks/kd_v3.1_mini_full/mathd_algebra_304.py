import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def verify() -> dict:
    checks = []
    proved_all = True

    # Verified proof: exact arithmetic equality in kdrag/Z3
    try:
        thm = kd.prove(91 * 91 == 8281)
        checks.append(
            {
                "name": "square_of_91_exact_equality",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove certified that 91*91 == 8281: {thm}",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "square_of_91_exact_equality",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check
    try:
        lhs = 91 ** 2
        rhs = 8281
        passed = lhs == rhs
        if not passed:
            proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": passed,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Computed 91**2 = {lhs}; compared against 8281 = {rhs}.",
            }
        )
    except Exception as e:
        proved_all = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical evaluation failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved_all, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)