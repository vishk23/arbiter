from kdrag.smt import *
import kdrag as kd


def verify():
    checks = []

    # Verified proof: for every positive integer m, there exists a positive integer n
    # such that m*n <= m+n. Choose n = 1.
    m = Int("m")
    n = Int("n")
    theorem = ForAll(
        [m],
        Implies(m > 0, Exists([n], And(n > 0, m * n <= m + n)))
    )
    try:
        proof = kd.prove(theorem)
        checks.append({
            "name": "existence_with_n_equals_1",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified theorem: {proof}",
        })
    except Exception as e:
        checks.append({
            "name": "existence_with_n_equals_1",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check: test concrete values with n = 1.
    sanity_ok = True
    examples = [1, 2, 5, 10, 100]
    for mm in examples:
        nn = 1
        if not (mm * nn <= mm + nn and nn > 0 and mm > 0):
            sanity_ok = False
            break
    checks.append({
        "name": "numerical_sanity_n_equals_1",
        "passed": sanity_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Checked sample positive integers m with n=1, verifying m*1 <= m+1.",
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)