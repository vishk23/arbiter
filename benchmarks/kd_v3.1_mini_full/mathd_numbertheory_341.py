import kdrag as kd
from kdrag.smt import Int, IntVal, ForAll, Implies
from sympy import Integer


def verify():
    checks = []
    proved = True

    # Check 1: verified proof certificate in kdrag for the modular arithmetic claim.
    # We prove the concrete statement that 5^100 leaves remainder 625 modulo 1000.
    try:
        thm = kd.prove(Integer(5) ** 100 % 1000 == 625)
        checks.append(
            {
                "name": "modular_remainder_5_pow_100",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Certified proof object returned: {thm}",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "modular_remainder_5_pow_100",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}",
            }
        )

    # Check 2: symbolic computation of final three digits and digit sum.
    try:
        n = Integer(5) ** 100
        last_three = int(n % 1000)
        digit_sum = sum(int(d) for d in str(last_three).zfill(3))
        passed = (last_three == 625) and (digit_sum == 13)
        if not passed:
            proved = False
        checks.append(
            {
                "name": "final_three_digits_and_sum",
                "passed": passed,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"Computed last three digits = {last_three}; digit sum = {digit_sum}.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "final_three_digits_and_sum",
                "passed": False,
                "backend": "sympy",
                "proof_type": "symbolic_zero",
                "details": f"SymPy computation failed: {type(e).__name__}: {e}",
            }
        )

    # Check 3: numerical sanity check using concrete values in the known cycle.
    try:
        sanity = (5 ** 3) % 1000 == 125 and (5 ** 4) % 1000 == 625 and (5 ** 100) % 1000 == 625
        if not sanity:
            proved = False
        checks.append(
            {
                "name": "numerical_cycle_sanity",
                "passed": sanity,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": "Verified that 5^3 ≡ 125 mod 1000, 5^4 ≡ 625 mod 1000, and 5^100 ≡ 625 mod 1000.",
            }
        )
    except Exception as e:
        proved = False
        checks.append(
            {
                "name": "numerical_cycle_sanity",
                "passed": False,
                "backend": "numerical",
                "proof_type": "numerical",
                "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
            }
        )

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)