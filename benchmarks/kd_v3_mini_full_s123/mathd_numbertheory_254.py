import kdrag as kd
from kdrag.smt import Int, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Verified proof: the remainder of the total number of marbles mod 10 is 6.
    try:
        total = 239 + 174 + 83
        # Z3-encodable certificate-style proof: the arithmetic identity is checked by kd.prove.
        # We prove the concrete statement that the remainder is 6.
        proof = kd.prove(total % 10 == 6)
        checks.append({
            "name": "total_marble_remainder_mod_10_is_6",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove established that (239 + 174 + 83) % 10 == 6; total={total}.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "total_marble_remainder_mod_10_is_6",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove remainder claim with kdrag: {e}",
        })

    # Numerical sanity check
    total = 239 + 174 + 83
    remainder = total % 10
    num_ok = (total == 496) and (remainder == 6)
    checks.append({
        "name": "numerical_sanity_total_and_remainder",
        "passed": num_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed total={total}, remainder={remainder}.",
    })
    if not num_ok:
        proved = False

    # Additional verified arithmetic check: residues add as expected.
    try:
        residue_check = kd.prove((239 % 10 + 174 % 10 + 83 % 10) % 10 == 6)
        checks.append({
            "name": "sum_of_residues_mod_10_is_6",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kd.prove established that (239 % 10 + 174 % 10 + 83 % 10) % 10 == 6.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "sum_of_residues_mod_10_is_6",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove residue-sum claim with kdrag: {e}",
        })

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)