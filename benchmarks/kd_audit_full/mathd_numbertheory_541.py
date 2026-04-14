from sympy import isprime

try:
    import kdrag as kd
    from kdrag.smt import Int, ForAll, Implies, And
    KDRAG_AVAILABLE = True
except Exception:
    KDRAG_AVAILABLE = False
    kd = None


def verify():
    checks = []
    proved = True

    # Verified proof check: if two positive integers multiply to 2005 and neither is 1,
    # then the only factor pair is (5, 401), hence the sum is 406.
    if KDRAG_AVAILABLE:
        a = Int("a")
        b = Int("b")
        # Z3 proves there are no other positive integer factor pairs via exhaustive arithmetic reasoning
        # over the divisors of 2005. We encode the exact claim directly.
        try:
            thm = kd.prove(
                ForAll([a, b],
                    Implies(
                        And(a > 0, b > 0, a * b == 2005, a != 1, b != 1),
                        a + b == 406
                    )
                )
            )
            checks.append({
                "name": "factor_pair_sum_is_406",
                "passed": True,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"Proved by kd.prove: {thm}"
            })
        except Exception as e:
            proved = False
            checks.append({
                "name": "factor_pair_sum_is_406",
                "passed": False,
                "backend": "kdrag",
                "proof_type": "certificate",
                "details": f"kdrag proof failed: {type(e).__name__}: {e}"
            })
    else:
        proved = False
        checks.append({
            "name": "factor_pair_sum_is_406",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": "kdrag not available in the runtime environment."
        })

    # Symbolic/number-theoretic support check: confirm 2005 = 5 * 401 and 401 is prime.
    prime_401 = bool(isprime(401))
    check2_passed = (2005 == 5 * 401) and prime_401
    checks.append({
        "name": "2005_factorization_and_401_prime",
        "passed": check2_passed,
        "backend": "sympy",
        "proof_type": "numerical",
        "details": f"2005 = 5 * 401 and isprime(401) returned {prime_401}."
    })
    proved = proved and check2_passed

    # Numerical sanity check: enumerate factor pairs of 2005.
    factor_pairs = []
    for x in range(2, 2006):
        if 2005 % x == 0:
            y = 2005 // x
            if x > 0 and y > 0:
                factor_pairs.append((x, y, x + y))
    sanity_passed = (factor_pairs == [(5, 401, 406), (401, 5, 406)])
    checks.append({
        "name": "numerical_factor_pair_enumeration",
        "passed": sanity_passed,
        "backend": "numerical",
        "proof_type": "numerical",
        "details": f"Positive factor pairs with both factors > 1: {factor_pairs}."
    })
    proved = proved and sanity_passed

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    import pprint
    pprint.pp(verify())