import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []

    # Certified modular inverse: 24 is the inverse of 2 modulo 47 because 2*24 = 48 ≡ 1 (mod 47)
    try:
        inv_proof = kd.prove((2 * 24 - 1) % 47 == 0)
        checks.append({
            "name": "inverse_of_2_mod_47",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified that 2*24 ≡ 1 (mod 47): {inv_proof}",
        })
    except Exception as e:
        checks.append({
            "name": "inverse_of_2_mod_47",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify modular inverse: {e}",
        })

    # Certified solution of the congruence: if 2n ≡ 15 (mod 47), then n ≡ 31 (mod 47)
    n = Int('n')
    try:
        thm = ForAll([n], Implies((2 * n - 15) % 47 == 0, (n - 31) % 47 == 0))
        cong_proof = kd.prove(thm)
        checks.append({
            "name": "solve_congruence",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified that 2n ≡ 15 (mod 47) implies n ≡ 31 (mod 47): {cong_proof}",
        })
    except Exception as e:
        checks.append({
            "name": "solve_congruence",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify congruence solution: {e}",
        })

    # Numerical sanity check: verify the proposed residue directly
    try:
        lhs = (2 * 31) % 47
        rhs = 15 % 47
        passed = lhs == rhs
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed (2*31) % 47 = {lhs} and 15 % 47 = {rhs}.",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)