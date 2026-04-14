import kdrag as kd
from kdrag.smt import *


def _pow_mod_check():
    # Verified modular arithmetic proof in Z3: the remainder is 9.
    # We prove the exact arithmetic identity by evaluating the concrete integers.
    return kd.prove((129**34 + 96**38) % 11 == 9)


def _congruence_sanity_check():
    # Simple concrete modular sanity check consistent with the proof.
    return (129 % 11 == 8) and (96 % 11 == 8)


def verify():
    checks = []
    proved = True

    # Check 1: certified proof of the remainder identity.
    try:
        prf = _pow_mod_check()
        checks.append({
            "name": "modular_remainder_identity",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove() returned proof: {prf}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "modular_remainder_identity",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proof failed: {type(e).__name__}: {e}",
        })

    # Check 2: numerical sanity check on residues.
    try:
        ok = _congruence_sanity_check()
        checks.append({
            "name": "residue_sanity",
            "passed": bool(ok),
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"129 % 11 = {129 % 11}, 96 % 11 = {96 % 11}",
        })
        proved = proved and bool(ok)
    except Exception as e:
        proved = False
        checks.append({
            "name": "residue_sanity",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Sanity check failed: {type(e).__name__}: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)