import kdrag as kd
from kdrag.smt import *


def verify():
    checks = []
    proved = True

    # Verified proof: 1529 = 254*6 + 5, hence 1529 mod 6 = 5.
    try:
        q = IntVal(254)
        lhs = IntVal(1529)
        rhs = q * IntVal(6) + IntVal(5)
        thm = kd.prove(lhs == rhs)
        checks.append({
            "name": "decomposition_1529_as_254_times_6_plus_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified equality proof: 1529 = 254*6 + 5. Proof: {thm}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "decomposition_1529_as_254_times_6_plus_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify decomposition 1529 = 254*6 + 5: {e}",
        })

    # Verified congruence theorem: if n = q*m + r then n mod m = r for this concrete case.
    try:
        # Directly prove the concrete modular fact using Z3 arithmetic.
        thm2 = kd.prove(IntVal(1529) % IntVal(6) == IntVal(5))
        checks.append({
            "name": "modulo_1529_mod_6_equals_5",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Certified modular remainder: 1529 mod 6 = 5. Proof: {thm2}",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "modulo_1529_mod_6_equals_5",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to certify 1529 mod 6 = 5: {e}",
        })

    # Numerical sanity check.
    try:
        numerical = (1529 - 254 * 6)
        passed = (numerical == 5) and (1529 % 6 == 5)
        if not passed:
            proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"1529 - 254*6 = {numerical}; Python modulo gives 1529 % 6 = {1529 % 6}.",
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {e}",
        })

    # Final result is proved only if every check passed.
    proved = all(ch["passed"] for ch in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)