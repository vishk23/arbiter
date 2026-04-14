import kdrag as kd
from kdrag.smt import Int


def verify() -> dict:
    checks = []

    # Certified proof that 194 = 11*17 + 7.
    # This is a direct arithmetic certificate, and it implies the remainder upon division by 11 is 7.
    try:
        proof_eq = kd.prove(194 == 11 * 17 + 7)
        passed_eq = True
        details_eq = f"kd.prove certified the equality: {proof_eq}"
    except Exception as e:
        proof_eq = None
        passed_eq = False
        details_eq = f"Proof failed for 194 = 11*17 + 7: {e}"

    checks.append({
        "name": "certificate_194_equals_11_times_17_plus_7",
        "passed": passed_eq,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details_eq,
    })

    # Certified modular remainder claim, encoded as an integer division fact.
    # Since 194 = 11*17 + 7 and 0 <= 7 < 11, the remainder of 194 mod 11 is 7.
    try:
        proof_mod = kd.prove(194 == 11 * 17 + 7)
        remainder = 194 % 11
        passed_mod = (remainder == 7)
        details_mod = (
            f"kd.prove certified the decomposition 194 = 11*17 + 7; "
            f"computed 194 % 11 = {remainder}."
        )
        if proof_mod is None:
            passed_mod = False
            details_mod = "Unexpectedly missing proof object."
    except Exception as e:
        passed_mod = False
        details_mod = f"Proof failed for modular remainder claim: {e}"

    checks.append({
        "name": "remainder_of_194_mod_11_is_7",
        "passed": passed_mod,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details_mod,
    })

    # Numerical sanity check at the concrete values.
    lhs = 194
    rhs = 11 * 17 + 7
    checks.append({
        "name": "numerical_sanity_194_equals_11_times_17_plus_7",
        "passed": lhs == rhs,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Checked 194 == 11*17 + 7: {lhs} == {rhs}.",
    })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)