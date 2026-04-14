import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: if n = 5k + 3, then 2n has remainder 1 modulo 5.
    n, k = Ints('n k')
    thm = ForAll([n, k], Implies(n == 5 * k + 3, (2 * n) % 5 == 1))
    try:
        proof = kd.prove(thm)
        checks.append({
            "name": "modular_double_remainder_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved: {proof}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "modular_double_remainder_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove theorem in kdrag: {e}",
        })

    # Numerical sanity check on a concrete instance: n = 8 = 5*1+3.
    try:
        n_val = 8
        remainder = (2 * n_val) % 5
        passed = (remainder == 1)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For n=8, 2n mod 5 = {remainder}.",
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)