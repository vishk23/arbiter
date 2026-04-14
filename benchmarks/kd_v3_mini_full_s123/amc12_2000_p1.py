import kdrag as kd
from kdrag.smt import *
from sympy import factorint, divisors


def verify():
    checks = []
    proved = True

    # Check 1: exact factorization of 2001 = 3 * 23 * 29
    try:
        fac = factorint(2001)
        passed = fac == {3: 1, 23: 1, 29: 1}
        checks.append({
            "name": "factorization_of_2001",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"factorint(2001) = {fac}; expected {{3:1, 23:1, 29:1}}",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "factorization_of_2001",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"sympy factorization failed: {e}",
        })
        proved = False

    # Check 2: exhaustive enumeration of all positive integer triples with product 2001
    # and verification that the maximal sum among distinct positive integers is 671.
    try:
        n = 2001
        triples = []
        for a in divisors(n):
            for b in divisors(n):
                if b < a:
                    continue
                ab = a * b
                if n % ab != 0:
                    continue
                c = n // ab
                if c < b:
                    continue
                triples.append((a, b, c, a + b + c))

        max_sum = max(t[3] for t in triples)
        max_triples = [t for t in triples if t[3] == max_sum]

        # The intended contest interpretation is the maximum among distinct positive integer triples.
        distinct_triples = [t for t in triples if len({t[0], t[1], t[2]}) == 3]
        distinct_max_sum = max(t[3] for t in distinct_triples)
        distinct_max_triples = [t for t in distinct_triples if t[3] == distinct_max_sum]

        passed = (
            distinct_max_sum == 671
            and (1, 3, 667, 671) in distinct_max_triples
            and all(t[3] <= 671 for t in distinct_triples)
        )
        checks.append({
            "name": "exhaustive_search_distinct_triples",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": (
                f"All triples count={len(triples)}; distinct max sum={distinct_max_sum}; "
                f"max distinct triples={distinct_max_triples}; "
                f"includes (1,3,667) with sum 671"
            ),
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "exhaustive_search_distinct_triples",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"enumeration failed: {e}",
        })
        proved = False

    # Check 3: verified proof certificate using kdrag for a concrete arithmetic fact.
    # This is a certificate-style proof that the exhibited triple works.
    try:
        thm = kd.prove(And(1 * 3 * 667 == 2001, 1 + 3 + 667 == 671))
        passed = hasattr(thm, "__class__")
        checks.append({
            "name": "certificate_for_witness_triple",
            "passed": passed,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kd.prove returned {type(thm).__name__} proving 1*3*667=2001 and sum=671",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "certificate_for_witness_triple",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof failed: {e}",
        })
        proved = False

    # Numerical sanity check
    try:
        candidate_sum = 1 + 3 + 667
        passed = (candidate_sum == 671) and (1 * 3 * 667 == 2001)
        checks.append({
            "name": "numerical_sanity_check",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"candidate (1,3,667) gives product {1*3*667} and sum {candidate_sum}",
        })
        proved = proved and passed
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"numerical check failed: {e}",
        })
        proved = False

    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)