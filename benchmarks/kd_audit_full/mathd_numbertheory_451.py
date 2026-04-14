from sympy import Symbol, Integer, factorint, isprime

try:
    import kdrag as kd
    from kdrag.smt import Int, IntVal, And, Or, Not, Implies, ForAll, Exists, Solver
except Exception:
    kd = None


def _is_prime_int(n):
    return bool(isprime(int(n)))


def verify():
    checks = []
    proved = True

    # Check 1: symbolic/math fact about exactly four divisors characterization, verified by direct exhaustive reasoning on the target range.
    # We certify the conclusion by enumerating all possible m with four divisors that can lead to sums in [2010, 2019].
    nice_values = []
    witnesses = {}
    for m in range(2, 3000):
        fac = factorint(m)
        num_divisors = 1
        for e in fac.values():
            num_divisors *= (e + 1)
        if num_divisors != 4:
            continue
        div_sum = sum(d for d in range(1, m + 1) if m % d == 0)
        if 2010 <= div_sum <= 2019:
            nice_values.append(div_sum)
            witnesses[div_sum] = m
    nice_set = sorted(set(nice_values))
    target_sum = sum(nice_set)
    proof_ok = (nice_set == [2016] and target_sum == 2016)
    checks.append({
        "name": "enumerate_four_divisor_witnesses_in_target_range",
        "passed": proof_ok,
        "backend": "sympy",
        "proof_type": "symbolic_zero",
        "details": f"Exhaustive check over m<3000 found only n=2016 in the target interval, with witness m={witnesses.get(2016)}; nice_set={nice_set}, sum={target_sum}."
    })
    proved = proved and proof_ok

    # Check 2: verified proof of a key divisibility fact used in the hint for the pq case.
    if kd is not None:
        try:
            p, q = Int("p"), Int("q")
            thm = kd.prove(
                ForAll([p, q], Implies(And(p % 2 == 1, q % 2 == 1), ((p + 1) * (q + 1)) % 4 == 0))
            )
            checks.append({
                "name": "odd_primes_imply_product_divisible_by_four",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kd.prove returned certificate: {thm}."
            })
        except Exception as e:
            checks.append({
                "name": "odd_primes_imply_product_divisible_by_four",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Could not construct proof: {type(e).__name__}: {e}"
            })
            proved = False
    else:
        checks.append({
            "name": "odd_primes_imply_product_divisible_by_four",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag backend unavailable in this environment."
        })
        proved = False

    # Check 3: numerical sanity check with explicit witness for 2016.
    p, q = 3, 503
    m = p * q
    divs = [1, p, q, m]
    s = sum(divs)
    numerical_ok = (_is_prime_int(p) and _is_prime_int(q) and s == 2016)
    checks.append({
        "name": "explicit_witness_2016_is_nice",
        "passed": numerical_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Witness m={m} has divisors {divs} summing to {s}; p and q are prime: {isprime(p)}, {isprime(q)}."
    })
    proved = proved and numerical_ok

    # Check 4: numerical sanity check that no p^3 case lands in the target range for primes around the threshold.
    pvals = [11, 13]
    sums = [1 + p + p*p + p*p*p for p in pvals]
    cubic_ok = (sums[0] < 2010 and sums[1] > 2019)
    checks.append({
        "name": "cubic_case_brackets_target_interval",
        "passed": cubic_ok,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"For p=11 sum={sums[0]} < 2010 and for p=13 sum={sums[1]} > 2019, bracketing the target interval."
    })
    proved = proved and cubic_ok

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)