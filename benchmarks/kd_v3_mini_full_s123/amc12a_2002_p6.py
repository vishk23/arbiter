import kdrag as kd
from kdrag.smt import *


def _build_proof():
    m = Int('m')
    n = Int('n')
    # For all positive integers m, there exists a positive integer n (namely n = 1)
    # such that m*n <= m+n.
    thm = kd.prove(
        ForAll(
            [m],
            Implies(
                m > 0,
                Exists([n], And(n > 0, m * n <= m + n))
            )
        )
    )
    return thm


def verify():
    checks = []

    # Verified proof check: Z3/Knuckledragger certificate for the existence statement.
    try:
        proof = _build_proof()
        checks.append({
            "name": "existential_witness_for_all_positive_m",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned proof: {proof}",
        })
    except Exception as e:
        checks.append({
            "name": "existential_witness_for_all_positive_m",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check: concrete witness n=1 works for sample positive m values.
    sample_ms = [1, 2, 5, 10, 123]
    num_passed = all(m * 1 <= m + 1 for m in sample_ms)
    checks.append({
        "name": "numerical_witness_sanity_check",
        "passed": num_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Checked m in {sample_ms} with witness n=1; inequality m*1 <= m+1 held for all samples.",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)