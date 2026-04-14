import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified proof: the sum 1+2+...+100 has remainder 4 mod 6.
    # We prove the exact arithmetic fact 5050 = 6*841 + 4, hence 5050 mod 6 = 4.
    try:
        thm = kd.prove(5050 == 6 * 841 + 4)
        checks.append({
            "name": "sum_1_to_100_mod_6_is_4_proof",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(thm),
        })
    except Exception as e:
        checks.append({
            "name": "sum_1_to_100_mod_6_is_4_proof",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Numerical / concrete sanity check: compute the exact sum and remainder.
    try:
        n = 100
        s = n * (n + 1) // 2
        rem = s % 6
        ok = (s == 5050) and (rem == 4)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"s={s}, s mod 6={rem}",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical check failed: {type(e).__name__}: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())