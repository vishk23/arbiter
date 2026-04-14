from sympy import factorint


def vp_fact(n, p):
    s = 0
    k = p
    while k <= n:
        s += n // k
        k *= p
    return s


def verify():
    checks = []
    proved = True

    # Check 1: exact factorization of 80325
    N = 80325
    fac = factorint(N)
    expected_fac = {3: 2, 5: 2, 7: 1, 17: 1}
    passed_fac = fac == expected_fac
    checks.append({
        "name": "factorization_of_80325",
        "passed": passed_fac,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"factorint(80325) = {fac}, expected {expected_fac}."
    })
    proved = proved and passed_fac

    # Check 2: numerical sanity check that 17! is divisible by 80325
    fact17 = 1
    for i in range(1, 18):
        fact17 *= i
    passed_num = (fact17 % N == 0)
    checks.append({
        "name": "numerical_sanity_17_factorial_divisible",
        "passed": passed_num,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"17! % 80325 = {fact17 % N}."
    })
    proved = proved and passed_num

    # Check 3: verified proof via a certificate-style construction using SymPy factorizations
    # We certify that 16! is not divisible by 80325 by comparing p-adic valuations.
    # This is a rigorous arithmetic certificate derived from Legendre's formula.
    exps16 = {p: vp_fact(16, p) for p in fac}
    passes_16 = all(exps16[p] >= e for p, e in fac.items())
    # For the least n, we need 16! not divisible, but 17! divisible.
    # The existence part is already checked numerically above; here we certify the lower bound.
    passed_cert = (not passes_16) and (vp_fact(16, 17) == 0)
    checks.append({
        "name": "certificate_lower_bound_via_legendre",
        "passed": passed_cert,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": (
            f"For n=16, valuations are {exps16}; since v_17(16!)=0 < 1, 80325 does not divide 16!. "
            f"Thus n >= 17."
        )
    })
    proved = proved and passed_cert

    # Check 4: exact valuation at n=17 suffices for each prime in factorization
    exps17 = {p: vp_fact(17, p) for p in fac}
    passed_17 = all(exps17[p] >= e for p, e in fac.items())
    checks.append({
        "name": "legendre_exponents_at_17",
        "passed": passed_17,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"v_p(17!) = {exps17}, which dominates the required exponents {fac}."
    })
    proved = proved and passed_17

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)