import kdrag as kd
from kdrag.smt import *
from sympy import Integer


def verify():
    checks = []

    # Verified symbolic proof that 119 is obtainable from two different primes
    # between 4 and 18: choose 11 and 13.
    try:
        p = Int("p")
        q = Int("q")
        theorem = Exists([p, q], And(
            p == 11,
            q == 13,
            p > 4,
            p < 18,
            q > 4,
            q < 18,
            p != q,
            And(
                p*q - (p + q) == 119,
                True,
            )
        ))
        prf = kd.prove(theorem)
        checks.append({
            "name": "existence_of_119_from_11_and_13",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"kdrag proof certificate obtained: {prf}",
        })
    except Exception as e:
        checks.append({
            "name": "existence_of_119_from_11_and_13",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove existence of 119 via kdrag: {type(e).__name__}: {e}",
        })

    # Symbolic exhaustive check over the finite set of primes between 4 and 18.
    try:
        primes = [5, 7, 11, 13, 17]
        values = []
        for i in range(len(primes)):
            for j in range(i + 1, len(primes)):
                p = Integer(primes[i])
                q = Integer(primes[j])
                values.append(int(p*q - (p + q)))
        passed = (119 in values) and all(v % 2 == 1 for v in values)
        checks.append({
            "name": "enumerate_all_possible_values",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Computed values for all prime pairs: {values}; 119 is present.",
        })
    except Exception as e:
        checks.append({
            "name": "enumerate_all_possible_values",
            "passed": False,
            "backend": "sympy",
            "proof_type": "symbolic_zero",
            "details": f"Enumeration failed: {type(e).__name__}: {e}",
        })

    # Numerical sanity check using the concrete pair (11, 13).
    try:
        p, q = 11, 13
        value = p * q - (p + q)
        passed = (value == 119)
        checks.append({
            "name": "numerical_sanity_11_13",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"For p=11, q=13, pq-(p+q) = {value}.",
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_11_13",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical sanity check failed: {type(e).__name__}: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    result = verify()
    print(result)