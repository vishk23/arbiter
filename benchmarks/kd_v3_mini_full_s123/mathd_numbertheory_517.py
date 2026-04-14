import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: the product is congruent to 2 modulo 4.
    # We encode the arithmetic identity directly in Z3 and prove it.
    try:
        thm = kd.prove((121 * 122 * 123) % 4 == 2)
        checks.append({
            "name": "modulo_4_residue_of_121_122_123",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove succeeded: {thm}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "modulo_4_residue_of_121_122_123",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove failed: {type(e).__name__}: {e}"
        })

    # Numerical sanity check.
    try:
        res = (121 * 122 * 123) % 4
        ok = (res == 2)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": ok,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"(121*122*123) % 4 = {res}"
        })
        if not ok:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {type(e).__name__}: {e}"
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)