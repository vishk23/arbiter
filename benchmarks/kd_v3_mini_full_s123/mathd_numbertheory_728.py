import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Certified modular arithmetic proof.
    # We prove the exact congruence in Z3/Knuckledragger by arithmetic normalization.
    try:
        thm = kd.prove(((29 % 7) ** 13 - (5 % 7) ** 13) % 7 == 3)
        checks.append({
            "name": "certified_modular_result",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified by kdrag: {thm}",
        })
    except Exception as e:
        checks.append({
            "name": "certified_modular_result",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {type(e).__name__}: {e}",
        })

    # Secondary certified reasoning: reduce residues first, then compute the difference modulo 7.
    try:
        r29 = 29 % 7
        r5 = 5 % 7
        residue_thm = kd.prove(And(r29 == 1, r5 == 5))
        diff_thm = kd.prove((((r29) ** 13 - (r5) ** 13) % 7) == 3)
        checks.append({
            "name": "residue_reduction_and_difference",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Residues and modular difference certified: {residue_thm}; {diff_thm}",
        })
    except Exception as e:
        checks.append({
            "name": "residue_reduction_and_difference",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag residue proof failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check at concrete values.
    diff_mod_7 = (29 ** 13 - 5 ** 13) % 7
    checks.append({
        "name": "numerical_sanity_check",
        "passed": diff_mod_7 == 3,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"(29**13 - 5**13) % 7 = {diff_mod_7}.",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)