from sympy import gcd
import kdrag as kd
from kdrag.smt import Int, And, Implies, ForAll


def verify():
    checks = []

    # Certified proof that 1058 is the inverse of 160 modulo 1399.
    # We prove the concrete arithmetic facts with kdrag/Z3.
    n = Int("n")
    proof_1 = kd.prove((160 * 1058 - 1) % 1399 == 0)
    checks.append({
        "name": "160_times_1058_congruent_1_mod_1399",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": f"kd.prove certified that (160*1058 - 1) % 1399 == 0. Proof: {proof_1}",
    })

    proof_2 = kd.prove(And(0 <= 1058, 1058 < 1399))
    checks.append({
        "name": "1058_in_required_range",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": f"kd.prove certified that 0 <= 1058 < 1399. Proof: {proof_2}",
    })

    # Exact uniqueness/existence condition via gcd.
    g = gcd(160, 1399)
    checks.append({
        "name": "gcd_is_one",
        "passed": bool(g == 1),
        "backend": "sympy",
        "proof_type": "certificate",
        "details": f"gcd(160, 1399) = {g}, so 160 has a unique inverse modulo 1399.",
    })

    # Certified theorem: if a number is congruent to 1 mod 1399 and in range,
    # then it is the modular inverse in the canonical residue class.
    m = Int("m")
    theorem = kd.prove(
        ForAll([m], Implies(And((160 * m - 1) % 1399 == 0, 0 <= m, m < 1399), m == 1058))
    )
    checks.append({
        "name": "uniqueness_of_inverse_in_canonical_range",
        "passed": True,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": f"kd.prove certified the uniqueness claim in the range [0, 1399). Proof: {theorem}",
    })

    # Numerical sanity check at the concrete value.
    n_val = 1058
    residue = (160 * n_val) % 1399
    checks.append({
        "name": "numerical_sanity_check",
        "passed": bool(residue == 1),
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"At n = {n_val}, (160*n) % 1399 = {residue}.",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)