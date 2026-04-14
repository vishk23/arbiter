from sympy import factorint, factorial


def verify():
    checks = []
    proved = True

    # Check 1: Exact prime factorization of 80325
    fac = factorint(80325)
    expected_fac = {3: 3, 5: 2, 7: 1, 17: 1}
    passed_fac = fac == expected_fac
    checks.append({
        "name": "prime_factorization_of_80325",
        "passed": passed_fac,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"factorint(80325) = {fac}, expected {expected_fac}."
    })
    proved = proved and passed_fac

    # Check 2: 17! is divisible by 80325
    n = 17
    f = factorial(n)
    passed_div = (f % 80325 == 0)
    checks.append({
        "name": "17_factorial_divisible_by_80325",
        "passed": passed_div,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"17! = {f}, and 17! mod 80325 = {f % 80325}."
    })
    proved = proved and passed_div

    # Check 3: 16! is not divisible by 80325 (shows minimality)
    f16 = factorial(16)
    passed_min = (f16 % 80325 != 0)
    checks.append({
        "name": "16_factorial_not_divisible_by_80325",
        "passed": passed_min,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"16! = {f16}, and 16! mod 80325 = {f16 % 80325}."
    })
    proved = proved and passed_min

    # Check 4: The least n is 17, justified by the prime factorization and divisibility check
    passed_least = passed_fac and passed_div and passed_min
    checks.append({
        "name": "least_n_is_17",
        "passed": passed_least,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": "80325 = 3^3 * 5^2 * 7 * 17, so n must be at least 17; 17! contains all required prime powers, while 16! does not contain the factor 17."
    })
    proved = proved and passed_least

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)