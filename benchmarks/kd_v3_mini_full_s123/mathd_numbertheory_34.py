import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Verified proof: show 9 * 89 ≡ 1 (mod 100) by direct arithmetic.
    try:
        proof = kd.prove((9 * 89 - 1) % 100 == 0)
        checks.append({
            "name": "modular_inverse_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove established that 9*89 ≡ 1 mod 100; proof={proof}",
        })
    except Exception as e:
        checks.append({
            "name": "modular_inverse_certificate",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Could not prove modular inverse certificate: {e}",
        })

    # Numerical sanity check: explicit residue computation.
    residue = (9 * 89) % 100
    checks.append({
        "name": "numerical_sanity",
        "passed": residue == 1,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed (9*89) % 100 = {residue}; expected 1.",
    })

    # Symbolic check: verify the residue is in the required range.
    checks.append({
        "name": "residue_range",
        "passed": 0 <= 89 <= 99,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": "Confirmed 89 is between 0 and 99 inclusive.",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)