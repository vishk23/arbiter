import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def verify():
    checks = []
    proved = True

    # Verified proof: 54 = 9*6 + 0, hence 54 mod 6 = 0.
    try:
        q = IntVal(9)
        r = IntVal(0)
        stmt = (IntVal(54) == q * IntVal(6) + r)
        proof = kd.prove(stmt)
        passed = True
        details = f"kd.prove certified 54 = 9*6 + 0; remainder r = 0. Proof: {proof}"
    except Exception as e:
        passed = False
        proved = False
        details = f"Could not certify decomposition 54 = 9*6 + 0 with kdrag: {e}"
    checks.append({
        "name": "decomposition_54_as_9_times_6_plus_0",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })

    # Verified modular consequence: 54 % 6 == 0.
    try:
        n = IntVal(54)
        d = IntVal(6)
        mod_thm = kd.prove(n % d == 0)
        passed = True
        details = f"kd.prove certified 54 % 6 == 0. Proof: {mod_thm}"
    except Exception as e:
        passed = False
        proved = False
        details = f"Could not certify 54 % 6 == 0 with kdrag: {e}"
    checks.append({
        "name": "remainder_of_54_mod_6_is_zero",
        "passed": passed,
        "backend": "kdrag",
        "proof_type": "certificate",
        "details": details,
    })

    # Numerical sanity check.
    remainder = int(Integer(54) % Integer(6))
    num_passed = (remainder == 0)
    if not num_passed:
        proved = False
    checks.append({
        "name": "numerical_sanity_check_54_mod_6",
        "passed": num_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Computed 54 % 6 = {remainder}; expected 0.",
    })

    return {"proved": proved and all(c["passed"] for c in checks), "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)