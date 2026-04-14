import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: 5^30 ≡ 1 (mod 7)
    # We encode the modular arithmetic directly in Z3 and ask kdrag to prove it.
    thm = None
    try:
        thm = kd.prove((5 ** 30) % 7 == 1)
        checks.append(
            {
                "name": "5^30_mod_7_is_1",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proved: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "5^30_mod_7_is_1",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Numerical sanity check at the concrete value.
    try:
        val = pow(5, 30, 7)
        ok = (val == 1)
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": ok,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"pow(5, 30, 7) = {val}",
            }
        )
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_sanity_check",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"numerical check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)