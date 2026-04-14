import kdrag as kd
from kdrag.smt import *


def _prove_remainder_mod_7():
    # Prove the concrete arithmetic claim using kdrag/Z3.
    # Sum_{k=0}^{100} 2^k = 2^101 - 1, and 2^101 mod 7 = 4, so the sum mod 7 = 3.
    s = sum(2 ** k for k in range(101))
    # Certificate proof that the computed concrete remainder is 3.
    return kd.prove(s % 7 == 3)


def verify():
    checks = []
    proved = True

    # Verified proof check via kdrag certificate.
    try:
        pf = _prove_remainder_mod_7()
        checks.append({
            "name": "sum_mod_7_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proved the concrete remainder statement with proof object: {pf}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sum_mod_7_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at concrete values.
    try:
        s = sum(2 ** k for k in range(101))
        remainder = s % 7
        passed = (remainder == 3)
        proved = proved and passed
        checks.append({
            "name": "numerical_remainder_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed remainder is {remainder}; expected 3.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_remainder_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)