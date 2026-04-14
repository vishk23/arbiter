import kdrag as kd
from kdrag.smt import Int, IntVal, ForAll, Implies, And


def verify():
    checks = []
    proved = True

    # Check 1: Verified certificate that 54 = 9*6 + 0, hence 54 mod 6 = 0.
    try:
        thm = kd.prove(IntVal(54) == IntVal(9) * IntVal(6) + IntVal(0))
        checks.append({
            "name": "decomposition_54_as_multiple_of_6",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved exact arithmetic identity: 54 = 9*6 + 0. Proof: {thm}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "decomposition_54_as_multiple_of_6",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove exact arithmetic identity 54 = 9*6 + 0: {e}"
        })

    # Check 2: Verified certificate that 54 is divisible by 6.
    try:
        q = Int("q")
        thm2 = kd.prove(ForAll([q], Implies(q == IntVal(9), IntVal(54) == q * IntVal(6))), by=[])
        # The theorem above is not the desired statement; instead we directly prove the concrete equality.
        # Use it as a sanity check that Z3 can certify the intended quotient.
        checks.append({
            "name": "quotient_certificate",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Verified quotient witness q=9 for 54 = 6*q. Proof: {thm2}"
        })
    except Exception as e:
        # If the quantified form is awkward, fall back to a direct arithmetic check via kdrag.
        try:
            thm2 = kd.prove(IntVal(54) == IntVal(6) * IntVal(9))
            checks.append({
                "name": "quotient_certificate",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Verified direct equality 54 = 6*9. Proof: {thm2}"
            })
        except Exception as e2:
            proved = False
            checks.append({
                "name": "quotient_certificate",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Failed to certify quotient witness for divisibility by 6: {e2}"
            })

    # Check 3: Numerical sanity check using Python modulo.
    try:
        remainder = 54 % 6
        passed = (remainder == 0)
        checks.append({
            "name": "numerical_modulo_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Computed 54 % 6 = {remainder}; expected 0."
        })
        if not passed:
            proved = False
    except Exception as e:
        proved = False
        checks.append({
            "name": "numerical_modulo_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical modulo computation failed: {e}"
        })

    # Final theorem statement as a verified arithmetic consequence.
    try:
        final_thm = kd.prove(IntVal(54) % IntVal(6) == IntVal(0))
        checks.append({
            "name": "final_remainder_is_zero",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Proved directly that 54 mod 6 = 0. Proof: {final_thm}"
        })
    except Exception as e:
        proved = False
        checks.append({
            "name": "final_remainder_is_zero",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 54 mod 6 = 0 directly: {e}"
        })

    proved = proved and all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)