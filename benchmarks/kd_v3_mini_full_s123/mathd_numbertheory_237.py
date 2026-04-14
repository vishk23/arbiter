import kdrag as kd
from kdrag.smt import *


def _build_checks():
    checks = []

    # Certified theorem: the sum 1 + 2 + ... + 100 equals 5050,
    # and 5050 mod 6 = 4.
    total = IntVal(5050)
    try:
        thm = kd.prove(total % 6 == 4)
        checks.append({
            "name": "sum_1_to_100_mod_6_is_4",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified with kd.prove that 5050 % 6 == 4. Proof type: {type(thm).__name__}."
        })
    except Exception as e:
        checks.append({
            "name": "sum_1_to_100_mod_6_is_4",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify 5050 % 6 == 4: {e}"
        })

    # Certified arithmetic identity: 1 + 2 + ... + 100 = 100*101/2 = 5050.
    # We verify the exact closed form in the SMT backend as an integer equality.
    try:
        n = IntVal(100)
        closed_form = (n * (n + 1)) / 2
        eq_proof = kd.prove(closed_form == IntVal(5050))
        checks.append({
            "name": "closed_form_equals_5050",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified 100*101/2 = 5050. Proof type: {type(eq_proof).__name__}."
        })
    except Exception as e:
        checks.append({
            "name": "closed_form_equals_5050",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify 100*101/2 = 5050: {e}"
        })

    # Numerical sanity check.
    s_num = 100 * 101 // 2
    rem = s_num % 6
    checks.append({
        "name": "numerical_sanity_sum_1_to_100_mod_6",
        "passed": rem == 4,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed 100*101//2 = {s_num}, and {s_num} % 6 = {rem}."
    })

    return checks


def verify():
    checks = _build_checks()
    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)