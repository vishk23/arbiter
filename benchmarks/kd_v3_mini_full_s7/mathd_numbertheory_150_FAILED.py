import sympy as sp
import kdrag as kd
from kdrag.smt import *


def _check_small_numerical_values():
    vals = [7 + 30 * n for n in range(1, 7)]
    primality = [sp.isprime(v) for v in vals]
    expected_vals = [37, 67, 97, 127, 157, 187]
    expected_primality = [True, True, True, True, True, False]
    passed = vals == expected_vals and primality == expected_primality
    details = f"values={vals}, primality={primality}"
    return passed, details


def _prove_n_is_6_by_factorization():
    n = Int('n')
    expr = 7 + 30 * n
    # Show the specific instance n=6 is composite by exhibiting factors.
    proof = kd.prove(187 == 11 * 17)
    return proof


def _prove_smallest_positive_n():
    n = Int('n')
    # For n = 1,2,3,4,5 the values are prime; n=6 gives a composite.
    # We verify the primality of the first five values with SymPy and the
    # compositeness of 187 by exact factorization.
    checks = []
    for k in range(1, 6):
        v = 7 + 30 * k
        checks.append(sp.isprime(v))
    if not all(checks):
        raise ValueError("Unexpected failure: one of 37,67,97,127,157 is not prime")
    # The smallest such N is then 6 because N=1..5 are prime and N=6 is composite.
    return 6


def verify():
    checks = []

    # Verified proof certificate: exact factorization of 187.
    try:
        proof = _prove_n_is_6_by_factorization()
        checks.append({
            "name": "factorization_187_eq_11_times_17",
            "passed": True,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": str(proof),
        })
    except Exception as e:
        checks.append({
            "name": "factorization_187_eq_11_times_17",
            "passed": False,
            "backend": "kdrag",
            "proof_type": "certificate",
            "details": f"Failed to prove 187 = 11*17: {e}",
        })

    # SymPy symbolic/computational verification that the first five cases are prime.
    try:
        vals = [7 + 30 * n for n in range(1, 6)]
        primality = [sp.isprime(v) for v in vals]
        passed = all(primality)
        checks.append({
            "name": "first_five_values_are_prime",
            "passed": passed,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"values={vals}, primality={primality}",
        })
    except Exception as e:
        checks.append({
            "name": "first_five_values_are_prime",
            "passed": False,
            "backend": "sympy",
            "proof_type": "numerical",
            "details": f"SymPy primality check failed: {e}",
        })

    # Numerical sanity check over N=1..6.
    try:
        passed, details = _check_small_numerical_values()
        checks.append({
            "name": "numerical_sanity_check_N_1_to_6",
            "passed": passed,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": details,
        })
    except Exception as e:
        checks.append({
            "name": "numerical_sanity_check_N_1_to_6",
            "passed": False,
            "backend": "numerical",
            "proof_type": "numerical",
            "details": f"Numerical check failed: {e}",
        })

    proved = all(c["passed"] for c in checks)
    return {"proved": proved, "checks": checks}


if __name__ == "__main__":
    print(verify())