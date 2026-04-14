import kdrag as kd
from kdrag.smt import *
from sympy import mod_inverse


def verify():
    checks = []
    proved = True

    # Verified proof: compute the modular inverse certificate in kdrag/Z3.
    n = Int("n")
    q = Int("q")
    # 24 is the inverse of 2 modulo 47 because 2*24 = 48 = 1 + 47
    inv_cert = kd.prove(2 * 24 == 1 + 47)
    # Use the certificate to show the residue claim is 31.
    # 15 * 24 = 360 = 31 + 7*47
    residue_cert = kd.prove(15 * 24 == 31 + 7 * 47)
    # Combined arithmetic check for the congruence solution.
    main_cert = kd.prove(ForAll([n], Implies((2 * n - 15) % 47 == 0, ((n - 31) % 47 == 0))))

    checks.append({
        "name": "inverse_of_2_mod_47",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": f"kd.prove() certified that 2*24 = 1 + 47, so 24 is the inverse of 2 modulo 47. Proof: {inv_cert}",
    })
    checks.append({
        "name": "residue_computation",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": f"kd.prove() certified that 15*24 = 31 + 7*47, hence 15*24 ≡ 31 (mod 47). Proof: {residue_cert}",
    })
    checks.append({
        "name": "congruence_solution",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": f"kd.prove() certified the congruence implication leading to n ≡ 31 (mod 47). Proof: {main_cert}",
    })

    # Numerical sanity check
    numeric_residue = (mod_inverse(2, 47) * 15) % 47
    checks.append({
        "name": "numerical_sanity",
        "passed": numeric_residue == 31,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed (inverse_mod(2,47) * 15) % 47 = {numeric_residue}.",
    })

    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())